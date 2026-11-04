"""Direct ctypes probe of KiCad's ngspice.dll: does a d_cosim instance parse and try to load its DLL?
Measured 2026-11-04 on KiCad 10.0.6 / ngspice-46: rc 0, message
"Instance: acs1   Message: d_cosim failed to load simulation binary C:/nonexistent/fake_rtl.dll", engine alive."""
import ctypes, os
K = r"C:\Users\yc012\AppData\Local\Programs\KiCad\10.0"
os.add_dll_directory(K + r"\bin")
dll = ctypes.CDLL(K + r"\bin\ngspice.dll")
lines = []
SEND = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p)
EXIT = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.c_bool, ctypes.c_int, ctypes.c_void_p)
@SEND
def send(s, i, p): lines.append(s.decode(errors="replace")); return 0
@SEND
def stat(s, i, p): return 0
@EXIT
def ex(st, imm, quit_, i, p): lines.append(f"<exit {st}>"); return 0
dll.ngSpice_Init(send, stat, ex, None, None, None, None)
for cm in ("analog", "digital", "xtraevt", "xtradev"):
    dll.ngSpice_Command(f"codemodel {K}/lib/ngspice/{cm}.cm".replace("\\", "/").encode())
deck = [b"d_cosim probe", b"v1 in 0 pulse(0 5 0 1n 1n 0.5m 1m)", b"abr1 [in] [din] adc1",
        b".model adc1 adc_bridge(in_low=1 in_high=4)", b"acs1 [din] [dout] cosim1",
        b'.model cosim1 d_cosim(simulation="C:/nonexistent/fake_rtl.dll")',
        b"adac1 [dout] [vout] dac1", b".model dac1 dac_bridge(out_low=0 out_high=5)", b"r1 vout 0 1k", b".end", None]
arr = (ctypes.c_char_p * len(deck))(*deck)
print("ngSpice_Circ rc:", dll.ngSpice_Circ(arr))
print("tran rc:", dll.ngSpice_Command(b"tran 10u 100u"))
for l in lines:
    if any(k in l.lower() for k in ("cosim", "error", "cannot", "load", "warning", "unknown", "exit", "fake")): print(" ", l[:220])
