# AoDNS

AoDNS, or Audio over DNS is a method of streaming data with TXT queries. 
The underlying concept is pretty simple basically there is a subdomain that gives the list of sequence number available and multiple sequence subdomains that holds the data.
This explained in more details below

Due to the module approach, this AoDNS implementation is easily extendable. 
You could for example add a new codec, add encryption, .... or anything else really, very easily.

Latency varies a lot depending on the configuration. 
If the client directly connects to the server, you can get away by using a small number of sequence same if proxied directly 

However, if you have a proxy that respect ttl, you'll need to increase the number of sequences that are available.
the TTL of the ``sequence`` endpoint is fixed to 10sec, and the TLL of the sequences domains is automatically calculated to be around 80% of the total time of audio data saved in all sequences

## How does it work
### Server
#### Capture
#### Compression (codec)
#### Encoding (asciializing)
#### Data ordering and packing
#### Conversion to TXT records
#### Sequence rotation

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

