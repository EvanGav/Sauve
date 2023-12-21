KEY="0qhau7ia8yi3d1tb07dq7xmrakpcaw9fefv6n3s0tmy117s4y8gk1n9cgnuqg5hbfppf6hjqnupxybpnrmneqbewijhdc8md5ihol8294f5q29kiea2uhgcpxqnylbe475876aqz8ki7ckx5x079z9s9w9ix1sqozjdivdfqe52kgdb3u7zze3ls9uwcea52bty0vgviufgtvpcxmivbk2l0bm84ujb2gmruoactm5a50znprye9to2zqcjc9ug4n044y9tyz2sj9xotjmssawn0x162ayc7w4c3xffdm13k3epv5zyok29c4pa77hcx"


# args : content_length, la longueur du contenu du fichier
#return : adjusted_key, la nouvelle clé permettant le XOR
def adjust_key_length(content_length):
    """
    Cette fonction ajuste la longueur de la clé en fonction de la longueur du contenu à chiffrer/déchiffrer.

    Args:
    - content_length (int): Longueur du contenu à chiffrer/déchiffrer.

    Returns:
    - str: Clé ajustée pour correspondre à la longueur du contenu.
    """
    key_length = len(KEY)
    # On calcule le nombre de répétitions de la clé
    repetitions = content_length // key_length
    # On calcule le nombre de caractères restants
    remaining = content_length % key_length
    # On ajuste la clé en fonction du nombre de répétitions et du nombre de caractères restants
    adjusted_key = KEY * repetitions + KEY[:remaining]
    return adjusted_key


def xor_encrypt_decrypt(content):
    """
    Cette fonction permet de chiffrer ou déchiffrer le contenu par opération XOR.
    
    Args :
    - content (bytes) : Le contenu à chiffrer ou déchiffrer
    
    Returns :
    - bytes : Le contenu chiffré ou déchiffré
    """
    # On ajuste la clé et on la transforme en une suite de bytes
    key_bytes = bytes(adjust_key_length(len(content)), 'utf-8')
    # On réalise le XOR entre chaque byte
    return bytes([a ^ b for a, b in zip(content, key_bytes)])
