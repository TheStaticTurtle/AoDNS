# AoDNS

AoDNS, or Audio over DNS is a method of streaming data with TXT queries. 
The underlying concept is pretty simple basically there is a subdomain that gives the list of sequence number available and multiple sequence subdomains that holds the data.
This explained in more details below

Due to the module approach, this AoDNS implementation is easily extendable. 
You could for example add a new codec, add encryption, .... or anything else really, very easily.

Latency varies a lot depending on the configuration. 
If the client directly connects to the server, you can get away by using a small number of sequence same if proxied directly 

However, if you have a proxy that respect ttl (which is most of them), you'll need to increase the number of sequences that are available.
the TTL of the ``sequence`` endpoint is fixed to 10sec, and the TLL of the sequences domains is automatically calculated to be around 80% of the total time of audio data saved in all sequences

## How does it work
### Server
#### Capture
Audio capture is done by default with pyaudio but can be extended to any source that supports arbitrary raw pcm frame lengths.

Because most codecs require a specific frame size, it is queried during setup and can not be changed

Sample rate and Channel count are also fixed but can be adjusted. Using the opus codec I was able to get 16kHz 1ch working.

#### Compression (codec)

Right now, two codec are implemented but only one officially tested:
- [Opus](https://opus-codec.org/) (tested, working)
- [Codec2](https://rowetel.com/codec2.html) **(untested)**

Opus provides a better audio quality than Codec2 but Codec2 will produce fewer data.

By default, AoDNS will use opus.

#### Encoding (asciializing)

Because dns TXT records and because of compatibility, the compressed audio frames needs to be converted to ascii chars.
Base64 will be the immediate choice of many but not the most space efficient one:
```repl
>>> t = "abcd"*64
>>> len(t)
256
>>> len(base64.b16encode(t.encode("utf-8")))
512
>>> len(base64.b32encode(t.encode("utf-8")))
416
>>> len(base64.b64encode(t.encode("utf-8")))
344
>>> len(base91.encode(t.encode("utf-8")))
315
```

Hence, why, by default base91 is used to encode the data

#### Data ordering and packing

TXT records only supports 255 bytes per string, however, a domain can have multiple TXT strings.

After some testing, it seems that 3k is approximately the maximum supported by the Windows server 2020 responder. 
Apparently some even support up to 4k.

To be on the safe side, by default one sequence domain will only store a maximum of 2kB

If you are using the client to connect directly to the server there would be an issue.
But AoDNS is able to work behind dns resolvers and unfortunately, some resolver will return the TXT strings in a random order:

```
# dig +ttlunit TXT seq_49680.music.example.com

;; ANSWER SECTION:
seq_49680.music.example.com. 21s IN TXT  "003'''8U|7E/J`Cc82|8XLpLk^T__5uf~F8PN7~Mfa(E^>WsjNBHV(<2AF|H<us_*}Dyt68)v%:^`<w?&OxM}_ZUf6S&KTbCtFQp$sD!]*a\""
seq_49680.music.example.com. 21s IN TXT  "001'''8U{OOU8]UVh.PiU!N=6WJ3k@>+fl&&<`>SnpY4Tzo_%W(Z_rs)@jzY1x|abYVng=d^vUg5cY\"+K~@OsihU3cxIyz+&MMQu!m,>=dHbsaD"
seq_49680.music.example.com. 21s IN TXT  "004'''rXSKF[23x}`Z!lP@HP8lDSWPhw^ViX!^CZHUgV9m=p}~kb5yk89@f*4/%Kk_!c2[{|\"d,~?B:u|RltK]Ce]t0zf5S{h6H;W"
seq_49680.music.example.com. 21s IN TXT  "005'''8Uy]!Pn!e%1J&xz;V,~d@7J%Ca#ct]D7B^U?u4|],2IE]7ZuE$9;2n;V~{UmwB8P;)=cU/LSdxGvNn>{PoBFUHx:&4]jrS^aDu{ve7)\"EU"
seq_49680.music.example.com. 21s IN TXT  "006'''8Uy]jZ/.]MJLfG%lrc[5FJuJ8$Ixk9VfRjLsLg*Hc`P!x1sHSZpIv5%Rf%|DfXm]%Lr}B%$lRn1oYmOZ+C|sM9bZi6&H+$NipeyS<>|bVvT"
seq_49680.music.example.com. 21s IN TXT  "007'''8Uq&l<\"!uR/i})@E]<TsXZ%0&ulQ%YB|p97tmV)mA|8[+M3;~G`XSu*cKo^Yg`Mq:JAiR{W*x`9mHe>e&?LfsL1!boJ^&\"[PPER0.("
seq_49680.music.example.com. 21s IN TXT  "008'''rX%=qo9rl2P@`BC!>T,O>(+ZU?hp}]WQT^MGki99SL18Ho[!yUL4]6jgEM*5eqkhMLs}fIwx&5N*^&XJv#0zG:5@vtC8|>[cO(.U_^WeFNFB"
seq_49680.music.example.com. 21s IN TXT  "009'''rX%=Ai]%`3:7z5swE1HMB9BS+7Wv@7\"w+nYNl&\"M_Z*6=T<p>Zp?Kwo|M},B;$Uwf`c~UrkLbUDuk8H69%},V}X>Ja~QRD"
seq_49680.music.example.com. 21s IN TXT  "010'''rXKK!74bs7GWw.mBS/@NVj7gCgGy_@sv*9+]tTvB;6a|*N*6Lr.fDcyb&sH2(f=_#zV?^Tb@H)De]<j^.4?3])hA"
seq_49680.music.example.com. 21s IN TXT  "011'''rXSK]\"hAk4R.zCnc{\";RBm[~,Kgl`kB]sxx^b=9PW&n.sK~1MWbOd[E:IdL`6Y%*3@>?`M2Sh^cmAH~3]3;[uJl`>5ITZUK5\"m!C"
seq_49680.music.example.com. 21s IN TXT  "012'''rX%=M5c+YU5JS`di#g7xy=;n~TrBLt*5FFhWpQ\"S#li//^[1xA*Wgsd]l+K~F1znI;<y30[Y2!A\"OlDY:d[)8_DAC"
seq_49680.music.example.com. 21s IN TXT  "013'''rXn;Erky{T>_HKk<OV2UD?wyYfEWMgbsJ?/HV;nMW,]`<O9Z*Wp[}<Z0n0.J4(KmD:(by2/187?oOsuL3_3}bUE2`xNjX[E1h4v%r\""
seq_49680.music.example.com. 21s IN TXT  "014'''8U{O%;Nl>EKbAo.w2?@(HJzsf(Ip9|Ac`rg1>hS!7tS(Uw68%gO#8M(Vf7>EZ.yN;zElg[Ga7(?_lMw%0y#d:oAa&)|6T3A>lB"
seq_49680.music.example.com. 21s IN TXT  "015'''}AP;v[(v.gHQHsjlM/I{`60)WHD9^ia*<Lgq&5.iY9lM8$::#;zCp)06W<lE>xi9.T;]hd3$!aKaCmhG8G7wR#D[<nZZJ<WP$"
seq_49680.music.example.com. 21s IN TXT  "016'''rX%=Nm;nn6uRG<,JM:A5/sQJ~>qB/<o:iu^\"sX]Z`n)oHv9lzqP%VEM5OsBW8LEP1mK\"CLAcDrK.|8%s)~)V%h33Kr,8$ba|KvB"
seq_49680.music.example.com. 21s IN TXT  "017'''rX$gRf8^ooNsOpLYL5Zy@(5%,j^*qG3K|L}/]G&#^1#;o]mRRiH13zyw_^jZ#w2%s`6Qg.wQDR<h?MAQ6!`43ov]+Ez&75b<?k0BH34QE"
seq_49680.music.example.com. 21s IN TXT  "018'''8U+O@Nv/(&nR|5&kW$m6}laH`p<Zp|LCx{t_lc1;!U6:.k!>.7I8`<y?*a#?(SvK@gRwV&WYs@gdzNOHc4<cst4>cBHw[/oG*E9@FZ=CN"
seq_49680.music.example.com. 21s IN TXT  "000'''8U{O#xvTKUK{a)`$*k0t`OwPP$B+(Ogky5*um7:PR2$UN1Q.{J!NZGWJ1~n=].^osw7&qGSY=sw)]WptNCJ;fO4e}d4ybQIXTTt]on*E"
seq_49680.music.example.com. 21s IN TXT  "002'''8U4}l=%kj@6Ph3j9aZJO*qQ,2R*m2z[Kp.;h:%m6);/CR)8J4l}Im9IU5)H+KGLT4T`,(Jt}JwBmEqxMw7[pCUYPO,8>T^9jl.[:w6)EG"
```

This is why all strings are prefixed with their index. The index and data is separated by 3 `'` which is a char not used in base91 

#### Sequence generation & rotation

The sequence generator is basically a way to index and store the packed data.
The number of stored packed data, directly affects the delay that the client will have.

On the other hand, having a low number of stored data will cause issues with the TTL of the records, especially to the `sequence` domain which is fixed to 10sec.

#### Conversion to DNS records

The records generator is a simple class that takes the sequence generator and frame size.

It will output a list of DNS records that the DNS server can then serve.
There will be `number_of_stored_packed_data + 1` records

The `sequence.music.example.com` is a TXT record with one string that holds all the available sequence numbers separated by `,`

Due to the max length of string being 255, the string is compressed with zlib and then base91 encoded.

Even with this protection there is a possibility that if the server is left running for long and the number of stored packed data is high that the server will crash because the data will be longer tha 255 chars. 

As the sequence numbers are linear on the server side, this could potentially be improved by sending the first sequence number and number of records.

##### TTL

TTL is a big issue, especially if the server is behind resolvers which might not respect low ttls.

The ttl of the `sequence.music.example.com` record is fixed to 10 seconds to ensure that it will be somewhat up to date before the client run out of sequences.

The ttl of sequence subdomains is dynamically calculated to be around 80% of the total length of audio data stored in all the records. Forumal looks like this: 
```python
seq_duration = (codec_frame_size * pack.frame_count) / (AUDIO_SAMPLE_RATE * AUDIO_CHANNELS * 2)
ttl = int(seq_duration * sequencer.max_concurrent_numbers * 0.8)
```

Which for the default settings and 75 sequence domains is around 23sec



### Client
#### Reading the sequence list
#### Reading sequences data
#### Sequence reconstruction
#### Sequence reading
#### Sequence reconstructor cleaning
#### Data un-packing and re-ordering
#### Decoding (de-asciializing)
#### Decompression (codec)
#### Playback

