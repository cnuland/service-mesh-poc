FROM registry.access.redhat.com/ubi8/python-36
# root to install flask
USER 0
COPY ./app /app
WORKDIR /app

USER 1000
# Launch flask instance on local host
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]
EXPOSE 5000