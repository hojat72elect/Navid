**fuzz testing** is simply providing invalid, unexpected, or random data as inputs to a computer program.

An effective fuzzer generates semi-valid inputs that are "valid enough" in that they are not directly rejected by the parser,
but do create unexpected behaviors deeper in the program and are "invalid enough" to expose corner cases that have not been properly dealt with.

Fuzzing systems are very good at finding certain types of vulnerabilities, including buffer overflow, denial of service (DoS), cross-site scripting, and code injection. 
However, they are less effective at dealing with silent security threats that do result in crashes or visible errors—such as spyware, worms, trojans, and rootkits.

While fuzzing is a simple technique, it is cost-effective and easy to scale. However, it does not provide a complete picture of security, quality, or effectiveness of a software product. 
