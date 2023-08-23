def create_packs(_array, pack_size):
    num_packs = len(_array) // pack_size
    if len(_array) % pack_size != 0:
        num_packs += 1

    packs = []
    for i in range(num_packs):
        start_idx = i * pack_size
        end_idx = start_idx + pack_size
        pack = _array[start_idx:end_idx]
        packs.append(pack)

    return packs
