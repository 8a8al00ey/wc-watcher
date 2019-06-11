IMAGE_NAME := soccerbot
RUN := docker run --rm -it -v `pwd`:/app --env-file=.env $(IMAGE_NAME)

build:
	docker build -t $(IMAGE_NAME) .

run:
	$(RUN)

run-shell:
	$(RUN) sh

run-daemon: build
	docker run -it -d --env-file=.env $(IMAGE_NAME)

stop:
	docker ps -a -q --filter ancestor=soccerbot | xargs --no-run-if-empty docker stop | xargs --no-run-if-empty docker rm -f

pull:
	git pull

redeploy: stop pull run-daemon
