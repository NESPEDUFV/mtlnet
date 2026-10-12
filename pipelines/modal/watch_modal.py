#!/usr/bin/env python3
"""Watch a running Modal lane from outside the container.

WHY THIS EXISTS
  `modal container logs <id>` returns EMPTY for a sandbox launched via submit_job: its stdout is
  captured and handed back at harvest time, so during a multi-hour run there is nothing to read.
  `modal app logs` shows only image builds. The job is therefore invisible by default.

  A mounted Volume, however, IS readable from outside -- but a reader sees only COMMITTED state.
  run_lane.sh's heartbeat writes to $LIVE_DIR on the volume and calls Volume.commit() after every
  sample, which is what makes the run observable.

  usage:  python watch_modal.py --state alabama --seed 7 [--follow] [--interval 60]
"""
import argparse, io, json, re, sys, time

import modal


# ONDE ISTO FUNCIONA. `vol.read_file()` exige uma conexao direta ao blob storage. Num terminal
# Claude Code isso funciona. No kernel Claude Science o proxy recusa:
#     ProxyError: 403 Forbidden (port <n> not allowed for host localhost)
# Verificado 2026-08-10 contra a lane florida_s7 EM EXECUCAO: read_file falhou nos dois arquivos,
# `vol.iterdir()` passou e mostrou o heartbeat crescendo (2413 B). Deste lado, portanto:
#   * sinal de vida sem custo: `vol.iterdir("/live/<estado>_s<seed>")` -- so nomes e tamanhos;
#   * conteudo: um job CPU de segundos, `tail -8 /data/live/<estado>_s<seed>/heartbeat.jsonl`.
# Este script continua sendo a ferramenta certa a partir de um terminal.
def read(vol, path):
    buf = io.BytesIO()
    try:
        for chunk in vol.read_file(path):
            buf.write(chunk)
    except Exception:
        return ""
    return buf.getvalue().decode("utf-8", "replace")


def show(vol, live, state, seed):
    hb = read(vol, f"{live}/heartbeat.jsonl").strip().splitlines()
    if not hb:
        print("  (no heartbeat yet -- the job may still be staging inputs)")
        return
    last = json.loads(hb[-1])
    gpu = last.get("gpu", "")
    print(f"  elapsed {last['t']:>6}s | cells_running={last['cells_running']} "
          f"folds_done={last['folds_done']} out={last['out_kb']}KB")
    if gpu:
        parts = gpu.split(",")
        if len(parts) >= 4:
            print(f"  gpu util={parts[0]}% mem={parts[1]}/{parts[2]}MiB temp={parts[3]}C"
                  + (f" throttle={parts[4]}" if len(parts) > 4 and parts[4] not in ("", "0x0000000000000000") else ""))
    # progress rate: folds per hour, and the ETA it implies
    if len(hb) > 2:
        first = json.loads(hb[0])
        dt, df = last["t"] - first["t"], last["folds_done"] - first["folds_done"]
        if df > 0 and dt > 0:
            per = dt / df
            print(f"  rate {per/60:.1f} min/fold -> remaining {(5-last['folds_done'])*per/60:.0f} min for 5 folds")
    lane = read(vol, f"{live}/lane.log").strip().splitlines()
    for ln in lane[-4:]:
        print(f"    {ln}")

    # ---- per-cell progress. WITHOUT THIS THE WATCHER IS MISLEADING ------------------------
    # The lane log only carries START/DONE, so between them it says nothing while `util` can sit
    # at 0 % for minutes. That combination reads exactly like a hung job and is not one: a cold
    # `torch.compile` spends its warm-up in inductor codegen and Triton autotuning, which are
    # CPU-bound, so the GPU really is idle and really is fine. Observed on alabama s100 joint:
    # batch 1 took 120 s, batches 2-9 then cost ~0 s each. The only way to tell "compiling" from
    # "stalled" is the trainer's own progress line, which the heartbeat already mirrors here.
    for fam in ("joint", "cat", "reg"):
        txt = read(vol, f"{live}/{state}_s{seed}_{fam}.out")
        if not txt.strip():
            continue
        prog = [l for l in txt.splitlines() if "batch" in l or "it/s" in l or "Epoch" in l]
        last = (prog or txt.splitlines())[-1].strip()
        print(f"  [{fam}] {last[:150]}")
        if prog:
            m = re.search(r"(\d+)/(\d+)\s*\[[^\]]*?([\d.]+)s?/batch", prog[-1])
            if m and float(m.group(3)) > 20:
                print("        ^ slow first batches + util 0% = torch.compile warm-up, not a stall")


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--state", required=True)
    a.add_argument("--seed", required=True)
    a.add_argument("--volume", default="poimtl-v18-data")
    a.add_argument("--follow", action="store_true")
    a.add_argument("--interval", type=int, default=60)
    args = a.parse_args()

    vol = modal.Volume.from_name(args.volume)
    live = f"live/{args.state}_s{args.seed}"
    while True:
        print(f"--- {time.strftime('%H:%M:%S')}  {args.state} seed {args.seed} ---")
        show(vol, live, args.state, args.seed)
        if not args.follow:
            return
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
