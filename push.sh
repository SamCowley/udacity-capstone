#!/bin/bash
pushd built
for file in *; do
    echo "==================================================================================="
    echo "Pushing: $(basename $file)"
    echo "==================================================================================="
    docker push samcowley/$file
done
popd
