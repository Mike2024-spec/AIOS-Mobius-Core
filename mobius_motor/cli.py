# mobius_motor/cli.py
# Λ-Möbius CLI – interfață de linie de comandă
import argparse
import json
import sys

from mobius_motor.core import motor_step
from mobius_motor.optimize import lambda_optimize

def cmd_step(args):
    val, st = motor_step(k=args.k, P=args.P, U=args.U, theta=args.theta)
    state_desc = {1: "Λ-Wrap", 0: "Λ-Steady", -1: "Λ-Unwrap"}[st]
    print(json.dumps({
        "k": args.k, "P": args.P, "U": args.U, "theta": args.theta,
        "value": val, "state": st, "state_desc": state_desc
    }, indent=2))

def cmd_optimize(args):
    if args.mode == "value":
        res = lambda_optimize(
            initial_guess=(args.k, args.P, args.U),
            theta=args.theta,
            mode="value",
            target=args.target,
            desired_state=args.desired_state,
        )
    else:
        res = lambda_optimize(
            initial_guess=(args.k, args.P, args.U),
            theta=args.theta,
            mode="state",
            desired_state=args.desired_state,
        )
    print(json.dumps(res, indent=2))

def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="mobius-cli",
        description="Λ-Möbius Core CLI"
    )
    subparsers = parser.add_subparsers(dest="command")

    # subcmd: step
    p_step = subparsers.add_parser("step", help="Run single motor step")
    p_step.add_argument("--k", type=float, required=True)
    p_step.add_argument("--P", type=float, required=True)
    p_step.add_argument("--U", type=float, required=True)
    p_step.add_argument("--theta", type=float, required=True)
    p_step.set_defaults(func=cmd_step)

    # subcmd: optimize
    p_opt = subparsers.add_parser("optimize", help="Run optimization")
    p_opt.add_argument("--k", type=float, default=1.0)
    p_opt.add_argument("--P", type=float, default=1.0)
    p_opt.add_argument("--U", type=float, default=5.0)
    p_opt.add_argument("--theta", type=float, required=True)
    p_opt.add_argument("--mode", choices=["value", "state"], required=True)
    p_opt.add_argument("--target", type=float, default=None)
    p_opt.add_argument("--desired_state", type=int, choices=[-1,0,1], default=None)
    p_opt.set_defaults(func=cmd_optimize)

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return
    args.func(args)

if __name__ == "__main__":
    main()
