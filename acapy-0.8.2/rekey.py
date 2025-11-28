from aries_askar import Store
import asyncio

async def rekey():
    new_key = Store.generate_raw_key(seed=b"12345678901234567890123456789012")
    # new_key = Store.generate_raw_key()
    print(f"New key: {new_key}")

    store = await Store.open(
        "postgres://postgres:mysecretpassword@postgres:5432/base_wallet",
        pass_key="",  # original passphrase
        key_method="kdf:argon2i:mod"
    )
    await store.rekey(
        pass_key=new_key, 
        key_method="kdf:argon2i:mod"
    )
    await store.close()
    print("Base wallet rekeyed successfully")

    store = await Store.open(
        "postgres://postgres:mysecretpassword@postgres:5432/tenancy_wallets",
        pass_key="",  # original passphrase
        key_method="kdf:argon2i:mod"
    )
    await store.rekey(
        pass_key=new_key, 
        key_method="kdf:argon2i:mod"
    )
    await store.close()
    print("Tenancy wallet rekeyed successfully")

loop = asyncio.get_event_loop()
loop.run_until_complete(rekey())
loop.close()