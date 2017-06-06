# Superscalar Processor
A simulator for a superscalar out-of-order processor that uses Tomasulo's algorithm in Python.

## How to Run

``` python superscalar.py <asm file> ```

## Processor Overview

![processor](http://imanmalik.com/assets/github/processor.png)

## Processor features

1. 4-way superscalar out-of-order execution Pipelined Execution with 4 stages: Fetch, Decode, Execute and Writeback
2. Multiple ALUs and Memory units and single Branch unit
3. Reservation station for each unit type (Tomasulo’s)
4. Static Branch Prediction - Always taken
5. Blocking issue with Branch instructions


## Additional files
Since I worked on this project incrementally, I have some useful files or those who wish to build their own simulator. I have included a simple processor that isn't pipelined in `simple.py`. A pipelined version of this proccessor is present in `pipeline.py`. I have also included my presentation slides. They include the results of some interesting experiments!


