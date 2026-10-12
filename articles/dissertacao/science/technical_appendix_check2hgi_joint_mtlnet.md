# Technical Appendix: Check2HGI and the Joint Multitask Architecture

This appendix specifies the representation model and the joint predictor used in the final study. It distinguishes the
self-supervised objective used to learn the hierarchical representations from the supervised objective used to train the
two prediction tasks. All dimensions, nonlinearities, and coefficients below correspond to the active implementation.

## 1. Check2HGI Representation Framework

### 1.1 Heterogeneous Graph Construction

#### Check-in records and hierarchy

A check-in is represented by the tuple

\[ c_i= (u_i,p_i,l_i,g_i,t_i). \]

Here, \(c_i\) is the \(i\)-th check-in, \(u_i\) is its user, \(p_i\) is its place, \(l_i= (\operatorname{lat}_
i,\operatorname{lon}_i)\) contains latitude and longitude, \(g_i\in\mathcal C\) is its place category, and \(t_i\) is
its timestamp. The active datasets use \(|\mathcal C|=7\) categories. Although \(g_i\) may denote a category or grid
descriptor in the general notation, it is the seven-class category in the implementation. The spatial region is derived
from \(l_i\) by a polygon-intersection join rather than stored as a separate component of the tuple.

The representation hierarchy is formalized as the heterogeneous graph

\[ \mathcal G= (\mathcal V,\mathcal E,\mathcal T_v,\mathcal T_e), \qquad \phi:\mathcal V\rightarrow\mathcal T_v, \qquad
\psi:\mathcal E\rightarrow\mathcal T_e. \]

Here, \(\mathcal V\) and \(\mathcal E\) are the node and edge sets, \(\mathcal T_v\) and \(\mathcal T_e\) are the
node-type and edge-type sets, and \(\phi\) and \(\psi\) map each node and edge to its type. The node types are
\(\mathcal T_v=\{C,P,R,\Omega\}\), where \(C\), \(P\), \(R\), and \(\Omega\) denote check-in, place, region, and city
types, respectively. Thus,

\[ \mathcal V=\mathcal V_C\cup\mathcal V_P\cup\mathcal V_R\cup\{v_\Omega\}. \]

Here, \(\mathcal V_C\), \(\mathcal V_P\), and \(\mathcal V_R\) are the mutually disjoint check-in, place, and region
node sets, and \(v_\Omega\) is the unique city node. A place is assigned to the polygon that intersects its coordinates;
places outside every polygon are removed during preprocessing.

#### Relation-specific edge sets

The edge set contains temporal, spatial, and hierarchical relations:

\[ \mathcal E= \mathcal E_{\mathrm{seq}} \cup\mathcal E_{C\rightarrow P} \cup\mathcal E_{\mathrm{sp}}^{P} \cup\mathcal
E_{P\rightarrow R} \cup\mathcal E_{\mathrm{adj}}^{R} \cup\mathcal E_{R\rightarrow\Omega}. \]

Here, \(\mathcal E_{\mathrm{seq}}\) contains temporal-succession edges between check-ins, \(\mathcal E_{C\rightarrow
P}\) contains check-in-to-place membership edges, \(\mathcal E_{\mathrm{sp}}^{P}\) contains spatial place-to-place
edges, \(\mathcal E_{P\rightarrow R}\) contains place-to-region membership edges, \(\mathcal E_{\mathrm{adj}}^{R}\)
contains region-adjacency edges, and \(\mathcal E_{R\rightarrow\Omega}\) connects each region to the city node. The
hierarchy is implemented through assignment vectors and segmented pooling rather than by materializing every membership
relation as a sparse adjacency matrix.

For each user, the check-ins are sorted by time. Consecutive visits are connected in both directions. Before global
rescaling, the temporal edge weight is

\[ \widetilde a_{ij}=\exp\!\left (-\frac{|t_j-t_i|}{3600}\right)
\quad\text{for}\quad (c_i,c_j)\in\mathcal E_{\mathrm{seq}}. \]

Here, \(\widetilde a_{ij}\) is the raw weight of a temporal edge from check-in \(c_i\) to check-in \(c_j\),
\(|t_j-t_i|\) is their separation in seconds, and \(3600\) is the one-hour decay constant. If the raw weights are
nonconstant, preprocessing applies global min-max normalization:

\[ a_{ij}=\frac{\widetilde a_{ij}-\widetilde a_{\min}} {\widetilde a_{\max}-\widetilde a_{\min}}. \]

Here, \(a_{ij}\) is the stored edge weight, and \(\widetilde a_{\min}\) and \(\widetilde a_{\max}\) are the minimum and
maximum raw temporal weights over the graph. If all raw weights are equal, they are left unchanged. The active check-in
graph contains only these user-succession edges. Same-place check-in edges and spatial edges lifted to the check-in
level exist as optional preprocessing modes but are inactive in the final configuration.

The place-level spatial graph \(\mathcal E_{\mathrm{sp}}^{P}\) is obtained from a Delaunay triangulation of place
coordinates. It is symmetrized and carries stored edge weights. The region graph \(\mathcal E_{\mathrm{adj}}^{R}\)
connects distinct polygons that intersect. The region convolution receives this adjacency without an explicit
edge-weight tensor.

No category-co-occurrence relation is materialized in the active graph:

\[ \mathcal E_{\mathrm{cat}}=\varnothing. \]

Here, \(\mathcal E_{\mathrm{cat}}\) denotes a hypothetical category-co-occurrence edge set and \(\varnothing\) is the
empty set. Category information instead enters as check-in node features and as the target of an auxiliary
place-reconstruction loss. A cosine similarity between region-level category histograms is computed, but it is used only
to select some negative regions during training. It is not used for message passing.

#### Feature initialization

The initial feature vector of check-in \(c_i\) is

\[ \mathbf f_i= \left[
\operatorname{onehot} (g_i); \sin\!\left (\frac{2\pi h_i}{24}\right); \cos\!\left (\frac{2\pi h_i}{24}\right); \sin\!\left (\frac{2\pi q_i}{7}\right); \cos\!\left (\frac{2\pi q_i}{7}\right)
\right]
\in\mathbb R^{11}. \]

Here, \(\mathbf f_i\) is the check-in feature vector, \(\operatorname{onehot} (g_i)\in\mathbb R^7\) is the one-hot
encoding of category \(g_i\), \(h_i\in\{0,\ldots,23\}\) is the hour of day, \(q_i\in\{0,\ldots,6\}\) is the day of week,
and the semicolon denotes vector concatenation. Stacking all \(N_C=|\mathcal V_C|\) feature vectors gives \(\mathbf
F\in\mathbb R^{N_C\times11}\).

### 1.2 Heterogeneous Message Passing and Layering

#### Relation-specific graph convolution

For an active homogeneous relation \(r\), a weighted graph-convolutional layer can be written as

\[ \operatorname{GCN} _{r}^{ (\ell)} (\mathbf H)
= \widehat{\mathbf D}_{r}^{-1/2} \widehat{\mathbf A} _{r} \widehat{\mathbf D}_{r}^{-1/2} \mathbf H\mathbf W_{r}^{
(\ell)} +\mathbf 1\mathbf b_{r}^{ (\ell)\top}. \]

Here, \(r\) identifies the temporal check-in graph, the Delaunay place graph, or the region-adjacency graph; \(\ell\) is
the layer index; \(\mathbf H\in\mathbb R^{N_r\times d_{\mathrm{in}}}\) is the input matrix for the \(N_r\) nodes of that
graph; \(\widehat{\mathbf A} _{r}\in\mathbb R^{N_r\times N_r}\) is its adjacency after the graph-convolution operator
adds self-loops; \(\widehat{\mathbf D}_{r}\in\mathbb R^{N_r\times N_r}\) is the corresponding diagonal degree matrix;
\(\mathbf W_{r}^{ (\ell)}\in\mathbb R^{d_{\mathrm{in}}\times d_{\mathrm{out}}}\) and \(\mathbf b_{r}^{ (\ell)}\in\mathbb
R^{d_{\mathrm{out}}}\) are relation- and layer-specific parameters; and \(\mathbf 1\in\mathbb R^{N_r}\) is an all-ones
vector. The implementation uses distinct graph-convolution modules at the check-in, place, and region levels. It does
not sum several relation matrices inside one relational-GCN layer.

The two-layer check-in encoder is

\[ \begin{aligned} \mathbf H_C^{ (1)} &=\operatorname{Drop} _{0.1}\!\left (\operatorname{PReLU}\!\left (
\operatorname{LN}\!\left (\operatorname{GCN}_{\mathrm{seq}}^{ (1)} (\mathbf F)
\right)\right)\right),\\ \mathbf H_C^{ (2)} &=\mathbf H_C^{ (1)}+ \operatorname{GCN}_{\mathrm{seq}}^{ (2)}\!\left
(\operatorname{LN} (\mathbf H_C^{ (1)})
\right). \end{aligned} \]

Here, \(\mathbf H_C^{ (1)},\mathbf H_C^{ (2)}\in\mathbb R^{N_C\times64}\) are the first- and second-layer check-in
states; \(\operatorname{GCN} _{\mathrm{seq}}^{ (1)}\) maps \(11\) features to \(64\); \(\operatorname{GCN}_
{\mathrm{seq}}^{ (2)}\) maps \(64\) to \(64\); \(\operatorname{LN}\) is layer normalization; \(\operatorname{PReLU}\) is
a learned parametric rectified linear unit shared across channels in this encoder; and \(\operatorname{Drop}_{0.1}\) is
dropout with probability \(0.1\). The second layer has no post-convolution activation or dropout. Its output is the
residual sum, which is dimensionally valid because both terms are in \(\mathbb R^{N_C\times64}\).

#### Attention pooling from check-ins to places

Let \(I_p=\{i:p_i=p\}\) denote the check-ins assigned to place \(p\). For each of four attention heads, the
implementation computes

\[ \begin{aligned} \mathbf q_h&= (\mathbf S\mathbf W_Q+\mathbf b_Q)_h,\\ \mathbf k_{ih}&= (\mathbf x_i\mathbf
W_K+\mathbf b_K)_h,\\ \mathbf v_{ih}&= (\mathbf x_i\mathbf W_V+\mathbf b_V)_h,\\ \alpha_{ih}&= \frac{\exp (\mathbf k_
{ih}^{\top}\mathbf q_h/\sqrt{64})} {\sum_{j\in I_p}\exp (\mathbf k_{jh}^{\top}\mathbf q_h/\sqrt{64})}, \qquad i\in I_p.
\end{aligned} \]

Here, \(h\in\{1,2,3,4\}\) is the head index; \(\mathbf S\in\mathbb R^{1\times64}\) is one learned seed query shared by
all places; \(\mathbf x_i=\mathbf H_C^{ (2)}[i,:]\in\mathbb R^{64}\) is the encoded check-in; \(\mathbf W_Q,\mathbf
W_K,\mathbf W_V\in\mathbb R^{64\times64}\) and their biases are learned projections; \(\mathbf q_h,\mathbf k_
{ih},\mathbf v_{ih}\in\mathbb R^{16}\) are head-specific slices; and \(\alpha_{ih}\) is a segmented softmax weight over
the check-ins of place \(p\). The divisor is \(\sqrt{64}\), exactly as implemented, rather than the conventional
\(\sqrt{16}\) based on head width.

The semantic place embedding is

\[ \mathbf e_p= \operatorname{PReLU}\!\left (\mathbf o_p+ \operatorname{ReLU} (\mathbf o_p\mathbf W_O+\mathbf b_O)
\right), \qquad \mathbf o_p=\mathbf q+\mathop{\Vert} _{h=1}^{4} \sum_{i\in I_p}\alpha_{ih}\mathbf v_{ih}. \]

Here, \(\mathbf e_p\in\mathbb R^d\) is the semantic embedding of place \(p\), with \(d=64\); \(\mathbf q\in\mathbb
R^{64}\) concatenates the four query heads; \(\Vert\) denotes head concatenation; \(\mathbf o_p\in\mathbb R^{64}\) is
the residual attention output; and \(\mathbf W_O\in\mathbb R^{64\times64}\) and \(\mathbf b_O\in\mathbb R^{64}\) define
the output projection. This pooling module has no layer normalization in the active configuration and no place-specific
attention bias.

#### Spatial place path and region aggregation

The region-oriented place representation is initialized by

\[ \mathbf E_P^{\mathrm{pre}} = \operatorname{sg} (\mathbf E_P^{\mathrm{sem}})
+\gamma\mathbf Q_P, \qquad \mathbf E_P^{\mathrm{sp}} = \operatorname{PReLU} _{64}\!\left (\operatorname{GCN}_
{\mathrm{sp}} (\mathbf E_P^{\mathrm{pre}})
\right). \]

Here, \(\mathbf E_P^{\mathrm{sem}}\in\mathbb R^{N_P\times64}\) stacks the semantic place embeddings \(\mathbf e_p\);
\(\operatorname{sg}\) is stop-gradient; \(\mathbf Q_P\in\mathbb R^{N_P\times64}\) is a trainable place table initialized
from remapped POI2Vec vectors; \(\gamma\in\mathbb R\) is a trainable scalar initialized to \(1.0\); \(\operatorname{GCN}
_{\mathrm{sp}}\) is one weighted \(64\)-to-\(64\) convolution over the Delaunay graph; and \(\operatorname{PReLU}_{64}\)
has one learned slope per output channel. The stop-gradient operator prevents the place-to-region and region-to-city
losses from updating the check-in encoder through this spatial branch.

Places are pooled within regions using the same four-head segmented-attention structure and the same \(\sqrt{64}\) score
divisor. If \(J_r=\{p:p\mapsto r\}\) is the set of places in region \(r\), the pre-convolution region vector is

\[ \widetilde{\mathbf z} _r = \mathbf q_R+ \mathop{\Vert}_{h=1}^{4} \sum_{p\in J_r}\beta_{ph}\mathbf v_{ph}, \qquad
\sum_{p\in J_r}\beta_{ph}=1. \]

Here, \(\widetilde{\mathbf z} _r\in\mathbb R^{64}\) is the pooled vector for region \(r\); \(\mathbf q_R\in\mathbb
R^{64}\) is the learned region-pooling seed after its query projection; \(\mathbf v_{ph}\in\mathbb R^{16}\) is the
projected place value for head \(h\); and \(\beta_{ph}\) is the segmented attention weight of place \(p\) within region
\(r\). The pooling block then adds a \(64\)-to-\(64\) rectified output projection, without layer normalization.

Spatial information is propagated between adjacent regions as

\[ \mathbf Z_R = \operatorname{PReLU} _{64}\!\left (\operatorname{GCN}_{\mathrm{adj}} (\widetilde{\mathbf Z}_R)
\right)
\in\mathbb R^{N_R\times64}. \]

Here, \(\widetilde{\mathbf Z} _R\in\mathbb R^{N_R\times64}\) stacks the pooled region vectors, \(\operatorname{GCN}_
{\mathrm{adj}}\) is one cached \(64\)-to-\(64\) graph convolution over polygon adjacency, \(\operatorname{PReLU}_{64}\)
is channelwise PReLU, and \(\mathbf Z_R\) contains the final region embeddings. Any not-a-number values produced for
empty groups are replaced with zero.

The city summary is an unnormalized area-weighted sum followed by a sigmoid:

\[ \mathbf z_\Omega = \sigma\!\left (\sum_{r=1}^{N_R}a_r\mathbf z_r \right)
\in\mathbb R^{64}. \]

Here, \(\mathbf z_\Omega\) is the city vector, \(\mathbf z_r=\mathbf Z_R[r,:]\in\mathbb R^{64}\) is the embedding of
region \(r\), \(a_r\) is that polygon's area, and \(\sigma\) is the elementwise logistic sigmoid. The coefficients
\(a_r\) are not normalized to sum to one.

#### Self-supervised objective

Each hierarchy boundary uses a learned bilinear discriminator:

\[ D_r (\mathbf a,\mathbf b)
= \sigma\!\left ((\mathbf a\mathbf W_r)\mathbf b^\top\right), \qquad \mathbf W_r\in\mathbb R^{64\times64}. \]

Here, \(D_r\) is the discriminator for boundary \(r\in\{C\!P,P\!R,R\!\Omega\}\); \(\mathbf a,\mathbf b\in\mathbb
R^{64}\) are a paired lower- and upper-level representation; \(\mathbf W_r\) is the boundary-specific bilinear matrix;
and \(\sigma\) is the logistic sigmoid.

For a set of positive and negative pairs, the boundary loss is

\[ \mathcal L_r = -\frac{1}{n_r}\sum_{j=1}^{n_r}\log (D_r^j+\varepsilon)
-\frac{1}{n_r}\sum_{j=1}^{n_r}\log (1-D_r^{j,-}+\varepsilon). \]

Here, \(\mathcal L_r\) is the loss at boundary \(r\), \(n_r\) is its number of pairs, \(D_r^j\) and \(D_r^{j,-}\) are
the positive and negative discriminator scores, and \(\varepsilon=10^{-7}\) is the numerical-stability constant. At the
check-in-to-place boundary, the negative is a uniformly sampled different place. At the place-to-region boundary, the
default negative is a different region; with probability \(0.25\), graphs with fewer than \(50{,}000\) places attempt to
draw a region whose category-histogram cosine similarity to the positive region is strictly between \(0.6\) and \(0.8\).
If no candidate exists, sampling remains random.

For the region-to-city boundary, the feature matrix is independently row-permuted while the temporal topology is
preserved:

\[ \mathbf F^{-}=\mathbf P_{\pi}\mathbf F. \]

Here, \(\mathbf F^{-}\in\mathbb R^{N_C\times11}\) is the corrupted feature matrix, \(\mathbf P_
{\pi}\in\{0,1\}^{N_C\times N_C}\) is the permutation matrix associated with a random permutation \(\pi\), and \(\mathbf
F\) is the original feature matrix. A second encoder pass produces corrupted region embeddings, which are contrasted
against the same positive city summary.

The auxiliary masked-place loss samples \(M\subseteq\mathcal V_P\) by masking each place independently with probability
\(0.15\), replaces the selected semantic place vectors by zero, mean-aggregates their Delaunay neighbors, and decodes
the aggregate through a \(64\rightarrow128\rightarrow7\) multilayer perceptron with PReLU. Its loss is

\[ \mathcal L_{\mathrm{mp}} = \frac{1}{|M|}\sum_{p\in M} \left[
\max\!\left (0, 1-\cos (\widehat{\mathbf y}_p,\mathbf y_p)
\right)
\right]^3. \]

Here, \(\mathcal L_{\mathrm{mp}}\) is the masked-place reconstruction loss, \(M\) is the sampled masked-place set,
\(\widehat{\mathbf y}_p\in\mathbb R^7\) is the decoder output, \(\mathbf y_p\in\mathbb R^7\) is the empirical mean
category one-hot vector of visits to place \(p\), and \(\cos\) is cosine similarity. The exponent is exactly \(3\).

The place-table anchor is

\[ \mathcal L_{\mathrm{anc}} = \frac{1}{64N_P} \left\|\mathbf Q_P-\mathbf Q_P^{ (0)}\right\|_F^2. \]

Here, \(\mathcal L_{\mathrm{anc}}\) is the anchor loss, \(\mathbf Q_P\in\mathbb R^{N_P\times64}\) is the trainable place
table, \(\mathbf Q_P^{ (0)}\in\mathbb R^{N_P\times64}\) is its fixed POI2Vec initialization, and \(\|\cdot\|_F\) is the
Frobenius norm. The normalization matches the elementwise mean used by the implementation.

The complete Check2HGI training objective is

\[ \boxed{ \mathcal L_{\mathrm{Check2HGI}} =0.4\mathcal L_{C\!P} +0.3\mathcal L_{P\!R} +0.3\mathcal L_{R\!\Omega}
+0.3\mathcal L_{\mathrm{mp}} +0.1\mathcal L_{\mathrm{anc}} }. \]

Here, \(\mathcal L_{\mathrm{Check2HGI}}\) is the scalar representation-learning loss; \(\mathcal L_{C\!P}\), \(\mathcal
L_{P\!R}\), and \(\mathcal L_{R\!\Omega}\) are the three boundary losses; \(\mathcal L_{\mathrm{mp}}\) is the
masked-place loss; and \(\mathcal L_{\mathrm{anc}}\) is the place-table anchor. The auxiliary coefficients are additive,
so the five coefficients are not intended to sum to one.

### 1.3 Embedding Fusion and Output Representation

The check-in output is the final row of the temporal check-in encoder:

\[ \mathbf x_i=\mathbf H_C^{ (2)}[i,:]\in\mathbb R^{d'}, \qquad d'=64. \]

Here, \(\mathbf x_i\) is the representation of check-in \(c_i\), \(\mathbf H_C^{ (2)}\) is the final check-in state
matrix, and \(d'\) is the check-in embedding width. Raw coordinates and the place embedding \(\mathbf e_{p_i}\in\mathbb
R^d\), with \(d=64\), are not concatenated directly into \(\mathbf x_i\). Instead, category and cyclic time features are
fused at the input of the temporal GCN, while coordinates determine the place and region spatial graphs. Hierarchical
boundary and reconstruction losses connect the levels during training. This distinction is essential: the implementation
is a hierarchical learning system, not a feature-concatenation encoder.

For the downstream joint model, the ordered history of user \(u\) is

\[ \mathbf H_u= (\mathbf x_1,\mathbf x_2,\ldots,\mathbf x_k)
\in\mathbb R^{k\times d'}, \qquad k=9,\quad d'=64. \]

Here, \(\mathbf H_u\) is the check-in sequence matrix, \(\mathbf x_j\) is the Check2HGI vector of the \(j\)-th
historical visit, and \(k=9\) is the fixed history length. A sliding window uses the first nine visits as input and the
tenth as the target, with stride one and a minimum user sequence length of ten.

The region task receives a separate lookup sequence:

\[ \mathbf R_u= (\mathbf z_{r (p_1)},\mathbf z_{r (p_2)},\ldots, \mathbf z_{r (p_k)})
\in\mathbb R^{9\times64}. \]

Here, \(\mathbf R_u\) is the region-modality sequence; \(r (p_j)\) maps visited place \(p_j\) to its region; and
\(\mathbf z_{r (p_j)}\in\mathbb R^{64}\) is the corresponding region embedding. The joint model therefore receives \(
(\mathbf H_u,\mathbf R_u)\), not a \(128\)-dimensional concatenation at each time step. Missing historical positions are
represented by all-zero vectors and detected by the model as padding.

## 2. Joint Multi-Task Learning Architecture

### 2.1 Shared Representation Backbone

#### Task-specific input encoders

For a batch of size \(B\), let \(\mathbf H\in\mathbb R^{B\times9\times64}\) denote the check-in input and \(\mathbf
R\in\mathbb R^{B\times9\times64}\) the region input. Each modality has an independent encoder with the same architecture
but different parameters:

\[ \begin{aligned} \mathbf U_m^{ (1)} &=\operatorname{Drop} _{0.1}\!\left (\operatorname{LN}\!\left (
\operatorname{ReLU} (\mathbf X_m\mathbf W_m^{ (1)}+\mathbf b_m^{ (1)})
\right)\right),\\ \mathbf U_m^{ (2)} &=\operatorname{Drop}_{0.1}\!\left (\operatorname{LN}\!\left (\operatorname{ReLU}
(\mathbf U_m^{ (1)}\mathbf W_m^{ (2)}+\mathbf b_m^{ (2)})
\right)\right),\\ \mathbf S_m^{ (0)} &=\operatorname{LN}\!\left (\operatorname{ReLU} (\mathbf U_m^{ (2)}\mathbf W_m^{
(3)}+\mathbf b_m^{ (3)})
\right). \end{aligned} \]

Here, \(m\in\{C,R\}\) identifies the category and region streams; \(\mathbf X_C=\mathbf H\) and \(\mathbf X_R=\mathbf
R\); \(\mathbf W_m^{ (1)}\in\mathbb R^{64\times256}\); \(\mathbf W_m^{ (2)},\mathbf W_m^{ (3)}\in\mathbb
R^{256\times256}\); the bias vectors have the corresponding output widths; and \(\mathbf U_m^{ (1)},\mathbf U_m^{ (2)
},\mathbf S_m^{ (0)}\in\mathbb R^{B\times9\times256}\). Although the constructor names two encoder layers, it appends a
final output projection. The executed encoder therefore contains three linear transformations per stream.

#### Bidirectional cross-attention

The interaction backbone contains two cross-attention blocks. For one block \(b\), category first reads region, and
region then reads the updated category stream:

\[ \begin{aligned} \mathbf A_b' &=\operatorname{LN} _{A,1}^{ (b)}\!\left (\mathbf A_b+ \operatorname{MHA}_{R\rightarrow
C}^{ (b)} (\mathbf A_b,\mathbf B_b,\mathbf B_b;\mathbf M_R)
\right),\\ \mathbf B_b' &=\operatorname{LN} _{B,1}^{ (b)}\!\left (\mathbf B_b+ \operatorname{MHA}_{C\rightarrow R}^{
(b)} (\mathbf B_b,\mathbf A_b',\mathbf A_b';\mathbf M_C)
\right),\\ \mathbf A_{b+1} &=\operatorname{LN} _{A,2}^{ (b)}\!\left (\mathbf A_b'+\operatorname{FFN}_{A}^{ (b)} (\mathbf
A_b')
\right),\\ \mathbf B_{b+1} &=\operatorname{LN} _{B,2}^{ (b)}\!\left (\mathbf B_b'+\operatorname{FFN}_{B}^{ (b)} (\mathbf
B_b')
\right). \end{aligned} \]

Here, \(b\in\{0,1\}\) is the block index; \(\mathbf A_0=\mathbf S_C^{ (0)}\) and \(\mathbf B_0=\mathbf S_R^{ (0)}\); all
stream tensors are in \(\mathbb R^{B\times9\times256}\); \(\operatorname{MHA} (\mathbf Q,\mathbf K,\mathbf V;\mathbf
M)\) is multi-head attention with query, key, value, and key-padding mask arguments; \(\mathbf M_C,\mathbf
M_R\in\{0,1\}^{B\times9}\) mark all-zero padded positions; and each \(\operatorname{LN}\) is a separate
layer-normalization module. In the active configuration, there is no stop-gradient, gate, identity substitution, or
zeroed key/value path.

Each cross-attention module uses four heads at width \(256\), so each head has width \(64\). For head \(h\),

\[ \operatorname{Attn} _h (\mathbf Q,\mathbf K,\mathbf V)
= \operatorname{softmax}\!\left (\frac{ (\mathbf Q\mathbf W_{Q,h})(\mathbf K\mathbf W_{K,h})^\top} {\sqrt{64}}+\mathbf M
\right)
(\mathbf V\mathbf W_{V,h}). \]

Here, \(h\in\{1,2,3,4\}\) is the head index; \(\mathbf W_{Q,h},\mathbf W_{K,h},\mathbf W_{V,h}\in\mathbb
R^{256\times64}\) are the head projections; \(\mathbf M\) is an additive attention mask with zero entries for valid keys
and negative infinity for padded keys; and \(\operatorname{softmax}\) is applied over key positions. The four head
outputs are concatenated and projected back to \(256\) dimensions. Attention dropout is \(0.15\).

The stream-specific feed-forward network is

\[ \operatorname{FFN} _{m}^{ (b)} (\mathbf Y)
= \operatorname{Drop}_{0.15}\!\left (\operatorname{Drop} _{0.15}\!\left (\operatorname{GELU} (\mathbf Y\mathbf W_{m,1}^{
(b)}+\mathbf b_{m,1}^{ (b)})
\right)
\mathbf W_{m,2}^{ (b)}+\mathbf b_{m,2}^{ (b)} \right). \]

Here, \(m\in\{C,R\}\) identifies the stream, \(\mathbf Y\in\mathbb R^{B\times9\times256}\), both \(\mathbf W_{m,1}^{
(b)}\) and \(\mathbf W_{m,2}^{ (b)}\) are in \(\mathbb R^{256\times256}\), the bias vectors are in \(\mathbb R^{256}\),
\(\operatorname{GELU}\) is the exact Gaussian error linear unit, and \(\operatorname{Drop}_{0.15}\) is dropout with
probability \(0.15\). Each direction has independent attention and feed-forward parameters.

After the two blocks, independent final normalizations produce

\[ \mathbf S_C=\operatorname{LN}_C (\mathbf A_2), \qquad \mathbf S_R=\operatorname{LN}_R (\mathbf B_2). \]

Here, \(\mathbf S_C,\mathbf S_R\in\mathbb R^{B\times9\times256}\) are the final category and region interaction streams,
and \(\operatorname{LN}_C\) and \(\operatorname{LN}_R\) are distinct learned normalizations. The implementation places
the complete cross-attention stack and these two normalizations in the optimizer's shared parameter group. At the
primitive layer level, however, the two tasks do not reuse one encoder, attention matrix, or feed-forward matrix.
Sharing occurs through coupled activations and a jointly optimized interaction subsystem.

During training, the two task loaders use the same user-disjoint fold but are independently shuffled. Consequently, a
category batch and region batch need not contain the same windows in the same order. The shorter loader is cycled to
match the longer loader. Validation is aligned. This is the active training contract; same-window aligned training is an
optional mode that is not enabled in the final runs.

### 2.2 Task-Specific Prediction Heads

#### Next-category head

The category stream is processed by a four-layer unidirectional GRU:

\[ \mathbf h_t^{ (\ell)} = \operatorname{GRU} _{\ell} (\mathbf s_t^{ (\ell)},\mathbf h_{t-1}^{ (\ell)}), \qquad
\ell\in\{1,2,3,4\}. \]

Here, \(t\in\{1,\ldots,9\}\) is the time index; \(\ell\) is the recurrent-layer index; \(\mathbf s_t^{ (1)}=\mathbf
S_C[:,t,:]\in\mathbb R^{B\times256}\); \(\mathbf s_t^{ (\ell)}=\mathbf h_t^{ (\ell-1)}\in\mathbb R^{B\times256}\) for
\(\ell>1\); and \(\mathbf h_t^{ (\ell)}\in\mathbb R^{B\times256}\) is the hidden state. The GRU applies dropout \(0.1\)
between recurrent layers and no recurrent dropout within a layer.

Let \(\tau_b\) be the last nonpadding position of batch item \(b\). The category logits are

\[ \boldsymbol\ell_b^{C} = \operatorname{Drop}_{0.1}\!\left(\operatorname{LN}(\mathbf h_{\tau_b}^{(4)})\right)
\mathbf W_C+\mathbf b_C \in\mathbb R^7. \]

Here, \(\boldsymbol\ell_b^{C}\) is the seven-class logit vector; \(\tau_b\) is the last valid time index; \(\mathbf h_
{\tau_b}^{(4)}\in\mathbb R^{256}\) is the top-layer GRU state for batch item \(b\); \(\mathbf W_C\in\mathbb
R^{256\times7}\) and \(\mathbf b_C\in\mathbb R^7\) are classifier parameters; and \(\operatorname{Drop}_{0.1}\) is
dropout with probability \(0.1\). The multiplication is dimensionally \((1\times256)(256\times7)=1\times7\).

#### Next-region dual-tower head

The region head has a private tower that processes the raw region sequence \(\mathbf R\in\mathbb R^{B\times9\times64}\)
and a shared-path tower that processes \(\mathbf S_R\in\mathbb R^{B\times9\times256}\). Both towers use the same adapted
spatio-temporal attention structure but have separate parameters. For tower \(q\in\{\mathrm{priv},\mathrm{shr}\}\),

\[ \begin{aligned} \mathbf T_q^{ (0)} &=\operatorname{Drop}_{\delta_q}\!\left (\operatorname{LN} (\mathbf X_q\mathbf
W_q^{\mathrm{in}}+\mathbf b_q^{\mathrm{in}})
\right),\\ \mathbf T_q^{ (1)} &=\mathbf T_q^{ (0)}+ \operatorname{SA}_q\!\left (\operatorname{LN} (\mathbf T_q^{ (0)})
;\mathbf B_q^{ (1)}\right),\\ \mathbf T_q^{ (2)} &=\mathbf T_q^{ (1)}+ \operatorname{FFN}_q\!\left (\operatorname{LN}
(\mathbf T_q^{ (1)})\right),\\ \mathbf f_q &=\operatorname{MatchAttn}_q\!\left (\operatorname{LN} (\mathbf T_q^{ (2)})
;\mathbf B_q^{ (2)},\tau \right). \end{aligned} \]

Here, \(q\) identifies the private or shared-path tower; \(\mathbf X_{\mathrm{priv}}=\mathbf R\) and \(\mathbf X_
{\mathrm{shr}}=\mathbf S_R\); \(\mathbf W_{\mathrm{priv}}^{\mathrm{in}}\in\mathbb R^{64\times128}\); \(\mathbf W_
{\mathrm{shr}}^{\mathrm{in}}\in\mathbb R^{256\times128}\); all \(\mathbf T_q^{ (j)}\in\mathbb R^{B\times9\times128}\);
\(\delta_{\mathrm{priv}}=0.3\) and \(\delta_{\mathrm{shr}}=0.1\); \(\operatorname{SA}_q\) is bidirectional multi-head
self-attention; \(\mathbf B_q^{ (1)},\mathbf B_q^{ (2)}\in\mathbb R^{H_q\times9\times9}\) are separate learned
pairwise-position biases initialized with ALiBi-style recency slopes; \(\operatorname{FFN} _q\) maps
\(128\rightarrow512\rightarrow128\) with GELU and tower dropout; \(\operatorname{MatchAttn} _q\) is a second
self-attention module that returns only the last valid query \(\tau\); and \(\mathbf f_q\in\mathbb R^{B\times128}\) is
the pooled tower feature. The private tower uses \(H_{\mathrm{priv}}=4\) heads, while the shared-path tower uses \(H_
{\mathrm{shr}}=8\) heads.

The two pooled features are fused additively:

\[ \mathbf f_R = \mathbf f_{\mathrm{priv}} +\beta\left (\mathbf f_{\mathrm{shr}}\mathbf W_{\mathrm{aux}}+\mathbf b_
{\mathrm{aux}}\right). \]

Here, \(\mathbf f_R,\mathbf f_{\mathrm{priv}},\mathbf f_{\mathrm{shr}}\in\mathbb R^{B\times128}\); \(\mathbf W_
{\mathrm{aux}}\in\mathbb R^{128\times128}\) and \(\mathbf b_{\mathrm{aux}}\in\mathbb R^{128}\) define the auxiliary
projection; and \(\beta\in\mathbb R\) is a trainable scalar initialized to \(0.1\). The scalar belongs to the region
optimizer group and receives the standard AdamW weight decay.

For a dataset with \(R_s\) region classes, the logits are

\[ \boldsymbol\ell_b^{R} = \operatorname{Drop}_{0.1}\!\left(\operatorname{LN}(\mathbf f_{R,b})\right)
\mathbf W_R+\mathbf b_R \in\mathbb R^{R_s}. \]

Here, \(\boldsymbol\ell_b^{R}\) is the next-region logit vector for item \(b\); \(R_s\) is read from the
dataset-specific region map; \(\mathbf f_{R,b}\in\mathbb R^{128}\) is its fused feature; \(\mathbf W_R\in\mathbb
R^{128\times R_s}\) and \(\mathbf b_R\in\mathbb R^{R_s}\) are classifier parameters; and
\(\operatorname{Drop}_{0.1}\) is dropout with probability \(0.1\). The multiplication is dimensionally
\((1\times128)(128\times R_s)=1\times R_s\). The code contains an optional transition-logit term
\(\alpha\log\mathbf T\), but the active model registers \(\alpha=0\) as a frozen buffer. Therefore, the transition
prior contributes exactly zero.

### 2.3 Multi-Task Optimization and Loss Fusion

For a category batch of size \(B_C\), the mean cross-entropy loss is

\[ \mathcal L_C = -\frac{1}{B_C}\sum_{b=1}^{B_C} \log \frac{\exp (\ell_{b,y_b^C}^{C})} {\sum_{j=1}^{7}\exp (\ell_
{b,j}^{C})}. \]

Here, \(\mathcal L_C\) is the next-category loss; \(B_C\) is the category batch size; \(y_b^C\in\{1,\ldots,7\}\) is the
true next category; and \(\ell_{b,j}^{C}\) is category logit \(j\) for item \(b\).

For a region batch of size \(B_R\), the mean cross-entropy loss is

\[ \mathcal L_R = -\frac{1}{B_R}\sum_{b=1}^{B_R} \log \frac{\exp (\ell_{b,y_b^R}^{R})} {\sum_{j=1}^{R_s}\exp (\ell_
{b,j}^{R})}. \]

Here, \(\mathcal L_R\) is the next-region loss; \(B_R\) is the region batch size; \(y_b^R\in\{1,\ldots,R_s\}\) is the
true next region; \(R_s\) is the region-class count; and \(\ell_{b,j}^{R}\) is region logit \(j\). Neither task uses
class weights, label smoothing, loss-scale normalization, knowledge distillation, or calibration in the active
objective.

The exact joint loss is the static scalarization

\[ \boxed{ \mathcal L_{\mathrm{total}} =0.75\mathcal L_C+0.25\mathcal L_R }. \]

Here, \(\mathcal L_{\mathrm{total}}\) is the scalar loss used for the single backward pass, \(\mathcal L_C\) is the mean
category cross-entropy, and \(\mathcal L_R\) is the mean region cross-entropy. No homoscedastic uncertainty weighting,
GradNorm, gradient surgery, alternating optimization, or dynamic task reweighting is active.

Three AdamW parameter groups are used. The category group contains the category encoder and GRU head; the region group
contains the region encoder and the entire dual-tower region head; and the shared group contains both cross-attention
blocks and the two final stream normalizations. Because the tasks are connected through cross-attention, each loss can
also update the opposite task encoder through key/value activations.

## 3. Implementation and Hyperparameter Specifications

### 3.1 Representation model

| Component                       | Active specification                                                                                     | Tensor transition or consequence        |
|---------------------------------|----------------------------------------------------------------------------------------------------------|-----------------------------------------|
| Check-in input                  | 7 category indicators plus 4 cyclic time features                                                        | \(11\) features per node                |
| Check-in encoder                | 2 weighted GCN layers, residual pre-normalization on layer 2                                             | \(11\rightarrow64\rightarrow64\)        |
| Check-in activation and dropout | Shared-slope PReLU; dropout \(0.1\) after layer 1 only                                                   | Output \(\mathbf x_i\in\mathbb R^{64}\) |
| Check-in-to-place pooling       | 4 heads, 16 dimensions per head, score scale \(\sqrt{64}\)                                               | \(N_C\times64\rightarrow N_P\times64\)  |
| Place spatial path              | Trainable \(N_P\times64\) table, \(\gamma_0=1.0\), one weighted Delaunay GCN, channelwise PReLU          | \(N_P\times64\rightarrow N_P\times64\)  |
| Place-to-region pooling         | 4 heads, score scale \(\sqrt{64}\), no layer normalization                                               | \(N_P\times64\rightarrow N_R\times64\)  |
| Region graph                    | One cached, unweighted \(64\rightarrow64\) GCN plus channelwise PReLU                                    | \(N_R\times64\rightarrow N_R\times64\)  |
| City aggregation                | Unnormalized area-weighted sum plus sigmoid                                                              | \(N_R\times64\rightarrow64\)            |
| Masked-place decoder            | Mask rate \(0.15\); neighbor mean; \(64\rightarrow128\rightarrow7\); PReLU; cubic scaled-cosine error    | Scalar auxiliary loss                   |
| Representation loss weights     | \(0.4,0.3,0.3\) for the three hierarchy boundaries; \(0.3\) masked-place; \(0.1\) anchor                 | Exact objective in Section 1.2          |
| Optimizer                       | Adam, learning rate \(10^{-3}\), weight decay \(0\), default betas \((0.9,0.999)\), epsilon \(10^{-8}\)  | Full-batch update                       |
| Training schedule               | 500 epochs; no learning-rate decay; no early stopping; best state minimizes the full-graph training loss | One update per epoch                    |
| Gradient control                | Global norm clipping at \(0.9\); no gradient accumulation; full precision                                | Deterministic seed \(42\)               |

### 3.2 Joint model

| Component                    | Active specification                                                                                                                                              | Tensor transition or consequence                         |
|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------|
| History construction         | Window \(k=9\), target at visit 10, stride 1, minimum sequence length 10, no synthetic tail                                                                       | \(9\times64\) per modality                               |
| Padding                      | All-zero \(64\)-vectors; all-zero time steps form the padding mask                                                                                                | Fixed sequence length 9                                  |
| Task encoders                | Separate encoders; Linear-ReLU-LN-Dropout, Linear-ReLU-LN-Dropout, Linear-ReLU-LN                                                                                 | \(64\rightarrow256\rightarrow256\rightarrow256\)         |
| Encoder dropout              | \(0.1\) after the first two linear blocks                                                                                                                         | No dropout after the third block                         |
| Interaction backbone         | 2 bidirectional cross-attention blocks                                                                                                                            | Two \(B\times9\times256\) streams                        |
| Cross-attention              | 4 heads, head width 64, attention dropout \(0.15\)                                                                                                                | Width preserved at 256                                   |
| Cross-attention FFNs         | Separate per stream and block; \(256\rightarrow256\rightarrow256\); GELU; dropout \(0.15\) after each linear stage                                                | Residual plus layer normalization                        |
| Category head                | Unidirectional GRU, input/hidden width 256, 4 layers, interlayer dropout \(0.1\); LN-Dropout-Linear classifier                                                    | \(B\times9\times256\rightarrow B\times7\)                |
| Private region tower         | Raw \(64\)-dimensional region sequence; model width 128; 4 heads; dropout \(0.3\); learned \(4\times9\times9\) bias per attention stage                           | \(B\times9\times64\rightarrow B\times128\)               |
| Shared-path region tower     | Interaction sequence width 256; model width 128; 8 heads; dropout \(0.1\); learned \(8\times9\times9\) bias per attention stage                                   | \(B\times9\times256\rightarrow B\times128\)              |
| Tower FFNs                   | \(128\rightarrow512\rightarrow128\), GELU, tower-specific dropout                                                                                                 | Width preserved at 128                                   |
| Fusion                       | \(\mathbf f_{\mathrm{priv}}+\beta\operatorname{Linear}(\mathbf f_{\mathrm{shr}})\), \(\beta_0=0.1\), trainable                                                    | \(B\times128\)                                           |
| Region prior                 | \(\alpha=0\), frozen; knowledge-distillation weight \(0\)                                                                                                         | No transition-prior contribution                         |
| Supervised objective         | Static weighted cross-entropy, category \(0.75\), region \(0.25\); no class weights                                                                               | One joint backward pass                                  |
| Optimizer                    | AdamW; weight decay \(0.05\); betas \((0.9,0.999)\); epsilon \(10^{-8}\)                                                                                          | Category, region, and shared groups                      |
| Peak learning rates          | Category \(10^{-3}\); region \(3\times10^{-3}\); shared \(3\times10^{-3}\) for Alabama, Arizona, and Florida, and \(10^{-3}\) for California, Texas, and Istanbul | Per-group OneCycle schedule                              |
| OneCycle schedule            | Per-group peak list; PyTorch default warmup fraction \(0.3\); one scheduler step per optimizer step                                                               | Shorter task loader cycles                               |
| Batch and duration           | Batch size 8192 per task loader; 50 epochs; accumulation 1                                                                                                        | Five user-disjoint folds                                 |
| Seeds                        | \(\{0,1,7,100\}\) for four-seed cells                                                                                                                             | Twenty seed-fold observations per fully repeated dataset |
| Gradient control             | Global norm clipping at \(1.0\)                                                                                                                                   | AdamW update follows clipping                            |
| Precision and execution      | Full precision training, TF32 enabled on supported CUDA devices, dynamic graph compilation enabled                                                                | No automatic mixed precision                             |
| Early stopping and selection | Early stopping disabled; minimum selectable epoch 0; joint selector is the geometric mean of category macro-F1 and region Accuracy@10                             | Selection uses both tasks                                |
| Training pairing             | Independently shuffled task loaders, maximum-size cycling; aligned validation                                                                                     | Cross-task training pairs need not be the same window    |

The number of region classes \(R_s\) is intentionally not hard-coded. It is read from each dataset's region map when the
task set is resolved, and it determines only the last classifier width and the region cross-entropy label space.

### 3.3 Implementation provenance

The mathematical specification above was checked against the following implementation points:

- [Check-in graph construction and features](../../../research/embeddings/check2hgi/preprocess.py)
- [Check-in residual graph encoder and masked-place decoder](../../../research/embeddings/check2hgi/model/variants.py)
- [Check-in-to-place attention pooling](../../../research/embeddings/check2hgi/model/Checkin2POI.py)
- [Hierarchical forward pass, spatial place path, discriminators, and representation loss](../../../research/embeddings/check2hgi/model/Check2HGIModule.py)
- [Frozen representation-building configuration](../../../scripts/probe/build_design_k_delaunay.py)
- [Region attention pooling and adjacency convolution](../../../research/embeddings/hgi/model/RegionEncoder.py)
- [Task encoders and head-parameter injection](../../../src/models/mtl/mtlnet/model.py)
- [Bidirectional cross-attention backbone](../../../src/models/mtl/mtlnet_crossattn/model.py)
- [Raw-region dual-tower routing](../../../src/models/mtl/mtlnet_crossattn_dualtower/model.py)
- [Four-layer category GRU as instantiated by the joint model](../../../src/models/next/next_gru/head.py)
- [Private and shared-path region towers and auxiliary fusion](../../../src/models/next/next_stan_flow_dualtower/head.py)
- [Static multitask loss](../../../src/losses/static_weight/loss.py)
- [AdamW parameter groups and per-group OneCycle schedule](../../../src/training/helpers.py)
- [Alabama, Arizona, and Florida learning-rate confirmation](../../../docs/studies/closing_data/perhead_lr_n20.md)
- [California and Texas final launcher](../../../docs/studies/closing_data/archive/run_logs/run_catx_v17_n20_h100.sh)
- [Istanbul final launcher](../../../docs/studies/closing_data/v17_completion/h3_istanbul/run_step3_n20.sh)

The dataset-specific shared learning rates in Section 3.2 follow the committed execution commands listed above. A
separate aggregate provenance note states that the shared peak was \(3\times10^{-3}\) for every run, but that statement
conflicts with the California, Texas, and Istanbul launchers, which explicitly set \(10^{-3}\). In the absence of the
remote saved run manifests in this checkout, the executable launch commands are treated as the stronger evidence for
reproduction.
