dat = bytes.fromhex(
    "70 69 7a 7a 61 70 69 7a "
    "7a 61 70 69 7a 7a 61 70 "
    "69 7a 7a 61 70 69 7a 7a"
)

key = bytes.fromhex(
    "1d 08 11 13 0f 17 49 15 "
    "0d 00 03 19 5a 1d 13 15 "
    "08 0e 5a 00 17 08 13 14"
)

secret = bytes([d ^ k for d, k in zip(dat, key)])
print(secret.decode())