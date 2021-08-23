#!/bin/bash
if grep -q '&all' <<< "${TRAVIS_COMMIT_MESSAGE}"; then
    CHANGED_DIRECTORIES="$(find ./containers -type d -maxdepth 1 -mindepth 1 | sort)"
else 
    COMMIT_RANGE="$(echo ${TRAVIS_COMMIT_RANGE} | cut -d '.' -f1,4 --output-delimiter '..')"
    CHANGED_FILES="$(git diff --name-only ${COMMIT_RANGE} --)"
    CHANGED_DIRECTORIES="$(echo "$CHANGED_FILES" | cut -d'/' -f-2 | sort | uniq | grep containers)"
fi

echo "==================================================================================="
echo "Commits: $COMMIT_RANGE"
echo "Changed Files:"
echo "$CHANGED_FILES"
echo "==================================================================================="
sed 's/^/Staged: /g' <<< "$CHANGED_DIRECTORIES"
echo "==================================================================================="

mkdir -p built

for DIR_PATH in $CHANGED_DIRECTORIES; do
    DIR="$(basename $DIR_PATH)"
    NAME="udacity-capstone-$DIR"
    echo "==================================================================================="
    echo "Building: $NAME"
    echo "==================================================================================="
    pushd $DIR_PATH
        docker build -t $NAME .
        docker tag $NAME samcowley/$NAME:latest
    popd
    touch built/$NAME
done
