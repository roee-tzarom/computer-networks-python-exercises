# TCP Sliding-Window Transfer Exercise

A Python socket exercise that sends a text payload in numbered chunks over a local TCP connection. The application adds its own handshake, chunk-size negotiation, acknowledgement messages and timeout-based resend logic on top of TCP.

## Implemented flow

1. `client.py` reads `tcp_sliding_window_transfer/config.txt`, connects to `127.0.0.1:12345` and performs the exercise's `SIN` / `SIN/ACK` exchange.
2. The client asks for the maximum message size, then splits the configured text file into chunks.
3. It sends up to `window_size` numbered `M<sequence>:<payload>` messages before waiting for ACKs.
4. The server acknowledges the highest consecutive sequence it has accepted. Its `drop_prob` setting can intentionally skip a chunk for demonstration.
5. On timeout, the client resumes at the oldest unacknowledged sequence.

## Run

Python 3 is required. Open two terminals in `tcp_sliding_window_transfer/`:

```bash
# Terminal 1
python server.py

# Terminal 2
python client.py
```

`config.txt` supplies the sample filename, window size, timeout, maximum message size and simulated drop probability. `payload_generator.py` can regenerate `sample_payload.txt` when run from the exercise directory.

This teaches an application-level sliding window; TCP itself already provides reliable ordered delivery. The custom parser assumes fixed-size payload chunks, so the included 700-character sample with `maximum_msg_size:100` is the intended demonstration. It is not a general binary-file transfer protocol.


## Protocol walkthrough

The exercise deliberately places message sequencing above a reliable TCP stream. The client reads a local configuration file, negotiates a maximum message size, and tracks the next sequence to send alongside the oldest sequence still awaiting acknowledgement. The server tracks the highest contiguous message received and responds with a cumulative ACK. The configurable drop probability skips application messages to expose the timeout and resend path during a local demonstration.

The message format is human-readable (`M<sequence>:<payload>`), which makes socket traces easier to inspect. The sender's window size controls how many messages can be outstanding. A timeout moves transmission back to the first unacknowledged message. The receiver does not reconstruct an arbitrary file format; the supplied fixed-size sample is the useful test case.

## Files and experiment

| File | Role |
| --- | --- |
| `tcp_sliding_window_transfer/client.py` | Configuration, connection, send window and retransmission |
| `tcp_sliding_window_transfer/server.py` | Handshake, simulated drops and cumulative acknowledgements |
| `tcp_sliding_window_transfer/config.txt` | Sample runtime settings |
| `tcp_sliding_window_transfer/payload_generator.py` | Recreates the example text payload |

Try the included configuration first, then increase the drop probability or reduce the timeout to observe additional retries. Start the server before the client. This project explains sliding-window bookkeeping; for transport-level reliability on top of an unreliable datagram service, see the [reliable UDP simulator](https://github.com/roee-tzarom/reliable-udp-network-simulator).
