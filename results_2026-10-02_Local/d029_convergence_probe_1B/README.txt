Side test made 2026-10-02 (about 03:35-03:46 JST) while the D029 run was going; it is not part of the D029 protocol.
Question: has the degree-preserving null settled by 32 x edges swaps on the sparser, restricted graphs of D029 (b)?
Command (repo root):
  python -m experiments.e1c_null_convergence --out <this folder> --graph-dir results_2026-10-02_Local/d029_survivor_restriction/graphs
      --graphs d029__fsS_1B d029__itS_1B d029__fsR1_1B --reps 8 --workers 6 --checkpoints 8 32 64 128 256
Read: summary.txt. The null mean of mutual pairs is flat from 8 x edges to 256 x edges on the three graphs (8 chains each).
The graph snapshots it read are results_2026-10-02_Local/d029_survivor_restriction/graphs/ (written before the null model started).
