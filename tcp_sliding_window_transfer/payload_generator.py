"""Create a deterministic sample payload for the transfer exercise."""

filename = "sample_payload.txt"
chunk_size = 100  # הגודל שהוגדר בשרת
num_chunks = 7  # הורדנו ל-7 (רק a עד g) - מספיק בשביל להדגים הזזה

with open(filename, "w") as f:
    for i in range(num_chunks):
        # מייצר את האות (a, b, c...)
        char = chr(ord('a') + i)

        # כותב את האות 100 פעמים
        f.write(char * chunk_size)

print(f"Created '{filename}' successfully with {num_chunks} chunks.")
print("This is enough to fill a window of 5 and slide it twice.")
