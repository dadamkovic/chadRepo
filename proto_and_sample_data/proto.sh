#!/bin/sh

set -e
cleanup() { :; }
trap cleanup EXIT

usage() {
	echo "usage: $0 <url to git repo>" >&2
	exit 1
}

[ "$1" ] || usage

# NOTE: the sonarqube instance needs to be running before the analysis request is made
# so this is not always quick enough, better starting it beforehand
# sonarqube=$(docker run -d -p 9000:9000 sonarqube)
# cleanup() {
	# docker rm -f "$sonarqube"
# }

git clone "$1"
repo=$(basename -s .git "$1")
cleanup() {
	rm -rf "$repo"
	# docker rm -f "$sonarqube"
}

docker run -it --rm --network host \
	-v "$PWD/$repo":/usr/src/mymaven -w /usr/src/mymaven sonar_maven \
	mvn clean verify sonar:sonar -Dsonar.host.url=http://localhost:9000 \
	-Dsonar.login=admin -Dsonar.password=admin

api='localhost:9000/api/issues/search?ps=500'

while [ xtrue = "x$(curl -u admin:admin "$api" | jq '.issues | length < 1')" ]
do
	echo waiting ...
	sleep 2
done

curl -u admin:admin "$api" |
	jq . |  # prettier format
	tee "$repo.sonar_data.json" |
	jq -r '
[.issues[] | {
	projectName: .project,
	creationDate,
	creationCommitHash: .hash,
	type,
	squid: .rule,
	component,
	severity,
	startLine: .textRange.startLine,
	endLine: .textRange.endLine,
	resolution,
	status,
	message,
	effort,
	debt,
	author
}] | (.[0] | keys_unsorted) as $header
	| $header, map(. as $row | $header | map($row[.]))[]
	| @csv
	' > "$repo.issues.csv"

