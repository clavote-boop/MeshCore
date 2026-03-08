#!/usr/bin/env python3
"""
MeshCore Emergency AI Failover System
Integrates: OpenWebUI (Open Claw) on N100 + Starlink + Ollama + MeshCore/GUZMAN
"""
import subprocess
import requests
import time
import os
import json
from datetime import datetime

# ============================================================
# CONFIGURATION - Update these for your N100 setup
# ============================================================
OPENWEBUI_URL = "http://localhost:3000"
OLLAMA_URL = "http://localhost:11434"
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
STARLINK_INTERFACE = "eth1"
PRIMARY_ISP_INTERFACE = "eth0"
MESHCORE_GUZMAN_CHANNEL = 2
PING_HOST = "8.8.8.8"

# ============================================================
# CONNECTIVITY CHECK - ISP -> Starlink -> Local Only
# ============================================================
def check_internet(interface=None):
  try:
    cmd = ["ping", "-c", "1", "-W", "2", PING_HOST]
    if interface:
      cmd += ["-I", interface]
      return subprocess.call(cmd, stdout=subprocess.DEVNULL) == 0
      except:
      return False
mp#t!}/]us
r/}b,i nt/iemnevo upty=t1h0o)n
3r
e"t"u"r
nM ers.hjCsoorne( )E[m"ecrhgoeincceys "A]I[ 0F]a[i"lmoevsesra gSey"s]t[e"mc
oInntteengtr"a]te
se:x cOeppetn:W
epbaUsIs 
(#O pFeanl lCblaacwk)  t+o  Sltoacralli nOkl l+a mOal loanm aN 1+0 0M
  etsrhyC:o
rre /=G UrZeMqAuNes
tDse.spiogsnte(df "f{oOrL LNA1M0A0_ UmRiLn}i/ aPpCi /wgietnhe rsaotlea"r,  pjoswoenr= {ba
                                                                                       c"kmuopde
                                                                                       l""":" 
                                                                                       "ilmlpaomrat3 "s,ub
                                                                                       p"rporcoemspst"
                                                                                       :i mpproormtp tr,eq
                                                                                       u"essttrsea
                                                                                       mi"m:p oFratl steim
                                                                                       e},
                                                                                        itmipmoerotu tj=s3o0n)

                                                                                        imrpeotrutr nl org.gjisnogn(
                                                                                        )i[m"proerstp oonss
                                                                                        ef"r]om
                                                                                         edxacteeptti mEex ciempptoirotn  daast eet:i
                                                                                         mreet
                                                                                         u
                                                                                         r#n  ──f "C[oLnOfCiAgLu rAaIt iUoNnA V──A──I──L──A──B──L──E──]── ──R──a──w── ──p──r──o──m──p──t──:── ──{──p
                                                                                         rPoRmIpMtA}R"Y_
                                                                                         I
                                                                                         S#P _=C=H=E=C=K= = = = === ="=8=.=8=.=8=.=8="==
                                                                                         =S=T=A=R=L=I=N=K=_=I=N=T=E=R=F=A=C=E= = = === ="=e=t=h=1="= = = = = = = = =  
                                                                                          ##  MSEtSaHrClOiRnEk  GrUoZuMtAeNr  CiHnAtNeNrEfLa cMeON
                                                                                          ISTTOARR L&I NRKE_SCPHOENCDK 
                                                                                           #   = = = === ="=1=9=2=.=1=6=8=.=1=0=0=.=1="= = =#= =S=t=a=r=l=i=n=k= =r=o=u=t=e=r= =g=a=t=e=w=a=y==
                                                                                           =O=L=L=A=M=A=_=U=R=L=  
                                                                                            d e f   s e n d _=t o"_hgtutzpm:a/n/(lmoecsaslahgoes)t::
                                                                                            1"1"4"3S4e"nd
                                                                                             OmPeEsNsWaEgBeU It_oU RGLU Z M A N   c h a=n n"ehlt tvpi:a/ /MleoschaClohroes tc:o3m0p0a0n"i o n#  pOrpoetno cColla"w" "on
                                                                                              pNr1i0n0t(
                                                                                              fC"L[AGUUDZEM_AANP]I _{UdRaLt e t i m e . n=o w"(h)t}t p>s>: /{/maepsis.aagnet[h:r1o3p3i]c}."c)om
                                                                                              /#v 1T/OmDeOs:s aIgnetse"gr
                                                                                              aMtEeS HMCeOsRhEC_oWrSe_ UBRLLE   c o m p a=n i"owns :p/r/oltooccaollh ohsetr:e80
                                                                                              8
                                                                                              0d"e f   m o#n iMteosrh_Caonrde_ rceosmppoanndi(o)n:

                                                                                              G"U"Z"MMAaNi_nC HlAoNoNpE L-_ ImDo n i t=o r2  G U Z M A N ,   r e s p o n d   w i t h   A I   f#a lGlUbZaMcAkN" "=" 
                                                                                              pprriionrti(t"y[ ScYhSaTnEnMe]l M
                                                                                              esOhLCLoArMeA _EMmOeDrEgLe n c y   A I   F a=i l"olvlearm aS3t"a r t i n g . . . " )    
                                                                                                 #w hLiolcea lT rfuael:l
                                                                                                 bcaocnkn emcotdieoln 
                                                                                                 =L OgGe_tF_IaLcEt i v e _ c o n n e c t i o=n (")/v
                                                                                                 aprr/ilnotg(/fm"e[sNhEcTo]r eA_cftaiivleo vceorn.nleocgt"io
                                                                                                 n
                                                                                                 :#  {──c oLnongegcitnigo ns}e"t)up
                                                                                                  i─f── ──c──o──n──n──e──c──t──i──o──n── ──=──=── ──"──P──R──I──M──A──R──Y
                                                                                                  _lIoSgPg"i:ng
                                                                                                  .pbraisnitc(C"o[nNfEiTg]( U
                                                                                                  sfiinlge nParmiem=aLrOyG _IFSIPL E-,>
 lCelvaeuld=el oAgIg ivniga. IONpFeOn,W
 efboUrIm"a)t=
 "e%l(iafs cctoinmnee)cst i[o%n( l=e=v e"lSnTaAmReL)IsN]K "%:(
 mpersisnatg(e")[sN"ET
 ]) 
 IlSoPg  D=O WlNo g-g>i nFga.igleotvLeorg gteor (S_t_anralmien_k_ )-
 >
  C#l a──u dCeo nAnIe"c)ti
  vsietnyd _cthoe_cgkusz m─a──n──(──"──[──N──E──T──-──A──L──E──R──T──]── ──I──S──P── ──d
  odwenf.  pSitnagr(lhionskt )a:c
  ttirvye:.
   rAeIs uolpte r=a tsiuobnparlo.c"e)ss
   .erluinf( c
   o[n"npeicntgi"o,n  "=-=c "",L O"C1A"L,_ O"L-LWA"M,A "":2"
   ,p rhionstt(]",[N
   EcTa]p tIunrtee_ronuettp uDtO=WTNr u-e>,  Ltoicmaelo uOtl=l5a
   m)a
    roent uNr1n0 0r eascutlitv.er"e)tu
    rsnecnodd_et o=_=g u0zm
    aenx(c"e[pNtE TE-xAcLeEpRtTi]o nI:n
    treertnuertn  dFoawlns.e 
    L
    odceafl  cAhIe c(kO_lplraimmaa/rNy1_0i0s)p (a)c:t
    irveet.u"r)n 
    peilnsge(:P
    RpIrMiAnRtY(_"I[SNPE_TC]H EACLKL) D
    O
    WdNe f- >c hMeecskh_Csotraer lhianrkd(w)a:r
    er eotnulryn" )pi
    nsge(nSdT_AtRoL_IgNuKz_mCaHnE(C"K[)NE
    T
    -dAeLfE RcTh]e cAkl_lo lilnatmear(n)e:t
     tdroyw:n
     .r  M=e srheCqourees tOsN.LgYe.t (Sfo"l{aOrL LpAoMwAe_rU ROLK}./"a)pi
     /ttiamges."s,l eteipm(e3o0u)t
     =
     3i)f 
     _r_entaumren_ _r .=s=t a"t_u_sm_aciond_e_ "=:= 
     2m0o0ni
     teoxrc_eapntd _Erxecseppotnido(n):
     return False

     def check_openwebui():
     try:
     r = requests.get(OPENWEBUI_URL, timeout=3)
     return r.status_code == 200
     except Exception:
     return False

     # ── Internet source selection ───────────────────────────────────
     def get_active_internet():
     if check_primary_isp():
     log.info("Internet: Primary ISP active")
     return "PRIMARY_ISP"
     elif check_starlink():
     log.info("Internet: Starlink fallback active")
     return "STARLINK"
     else:
     log.warning("Internet: ALL DOWN - local only mode")
     return "NONE"

     # ── AI source selection ─────────────────────────────────────────
     def get_ai_response(prompt, api_key=None):
     internet = get_active_internet()
     if internet in ("PRIMARY_ISP", "STARLINK"):
     # Try OpenWebUI (Open Claw) first on N100
     
def get_active_connection():
  if check_internet(PRIMARY_ISP_INTERFACE):
    return "PRIMARY_ISP"
elif check_internet(STARLINK_INTERFACE):
return "STARLINK"
elif check_ollama():
return "LOCAL_OLLAMA"
return "MESHCORE_ONLY"

def check_ollama():
  try:
    r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
return r.status_code == 200
except:
return False

# ============================================================
# AI RESPONSE - Claude -> OpenWebUI -> Ollama fallback
# ============================================================
def get_ai_response(prompt, connection):
  if connection in ["PRIMARY_ISP", "STARLINK"]:
    try:
      # Use OpenWebUI (Open Claw) API on N100
      r = requests.post(f"{OPENWEBUI_URL}/api/chat", json={
        "model": "claude-3-5-sonnet",
        "messages": [{"role": "user", "content": pro
