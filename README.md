# TCP Sliding-Window Transfer

A local Python client and server that make acknowledgement, window and retransmission state visible while moving a text payload. The transport is TCP; the numbered messages and resend policy are implemented at the application layer so their behavior can be studied directly.

## Transfer flow

1. The client reads settings from `tcp_sliding_window_transfer/config.txt` and connects to `127.0.0.1:12345`.
2. Client and server exchange `SIN`, `SIN/ACK` and `ACK` messages, then negotiate the maximum chunk size.
3. The client reads the configured text file, splits it into chunks and sends up to `window_size` outstanding messages in the form `M<sequence>:<payload>`.
4. The server accepts the next expected sequence and replies with a cumulative `ACK<number>`. Its configurable drop probability can skip a message in the application logic.
5. If an acknowledgement does not arrive before the timeout, the client resumes sending from the oldest unacknowledged chunk.

```text
text file → numbered chunks → send window → TCP connection
                                         ← cumulative ACKs
```

## Run locally

Python 3 and two terminals are sufficient. From the repository root:

```bash
# Terminal 1
cd tcp_sliding_window_transfer
python server.py

# Terminal 2
cd tcp_sliding_window_transfer
python client.py
```

The included `sample_payload.txt` is the default input. The client reports progress and completion in the terminal; the receiver does not write a reconstructed output file. Run `python payload_generator.py` from the same directory if you want to recreate the sample payload.

## Configuration

| Setting | Default | Effect |
| --- | --- | --- |
| `message` | `sample_payload.txt` | Text file read by the client |
| `maximum_msg_size` | `100` | Chunk length supplied by the server |
| `window_size` | `5` | Maximum unacknowledged messages sent by the client |
| `timeout` | `3` | Client wait time before resending |
| `drop_prob` | `0.0` | Probability that the server deliberately skips a message |

Increase `drop_prob` to observe retransmissions. Keep the sample payload and maximum size aligned with the parser's fixed-size chunk assumption.

## Code map

- `tcp_sliding_window_transfer/client.py` handles configuration, chunking, the send window and retries.
- `tcp_sliding_window_transfer/server.py` handles connection setup, sequence tracking and acknowledgements.
- `tcp_sliding_window_transfer/payload_generator.py` creates local demonstration data.

TCP already provides reliable ordered byte delivery. This project adds visible application-level sequencing for learning; its simple text framing is not designed for arbitrary binary transfers or production use.
