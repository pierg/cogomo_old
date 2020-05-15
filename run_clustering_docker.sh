
# To modfiy the mission in input modify the input_clustering.py in ./output
docker run  -it \
            -v "$(pwd)/output":/home/cogomo/output \
            pmallozzi/cogomo:latest