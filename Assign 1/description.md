/* Initially,  m numbers are distributed to m processes, respectively.*/

For each process with odd rank P, send its number to the process with rank P-1.

For each process with rank P-1, compare its number with the number sent by the process with rank P and send the larger one back to the process with rank P.

For each process with even rank Q, send its number to the process with rank Q-1.

For each process with rank Q-1, compare its number with the number sent by the process with rank Q and send the larger one back to the process with rank Q.

Repeat 1-4 until the numbers are sorted.
