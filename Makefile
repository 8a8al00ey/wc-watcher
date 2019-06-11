IMAGE_NAME := soccerbot
RUN_CMD := -it --env-file=.env -h `hostname`
RUN := docker run --rm -v `pwd`:/app $(RUN_CMD) $(IMAGE_NAME)

build:
	docker build -t $(IMAGE_NAME) .

run:
	$(RUN)

shell:
	$(RUN) sh

run-daemon: build
	docker run -d $(RUN_CMD) $(IMAGE_NAME)

stop:
	docker ps -a -q --filter ancestor=soccerbot | xargs --no-run-if-empty docker stop | xargs --no-run-if-empty docker rm -f

pull:
	git pull

redeploy: stop pull run-daemon
