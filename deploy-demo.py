import commands
services=5
for i in range(0, services):
    oc=commands.getstatusoutput("oc process -f deploy.yaml -p SERVICES={} -p IDENTITY={} | oc create -f -".format(services, i))