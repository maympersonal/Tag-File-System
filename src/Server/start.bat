 docker run --rm --name server_miguel1 --cap-add NET_ADMIN --network servers --ip 10.0.11.2 -itd server_miguel
 docker run --rm --name server_miguel2 --cap-add NET_ADMIN --network servers --ip 10.0.11.3 -itd server_miguel
 docker run --rm --name server_miguel3 --cap-add NET_ADMIN --network servers --ip 10.0.11.4 -itd server_miguel
