pragma circom 2.0.0;

template Add3() {
    signal input a;
    signal input b;
    signal input c;
    signal output sum;

    sum <== a + b + c;
}

component main = Add3();
