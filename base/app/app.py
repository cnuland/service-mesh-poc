from flask import Flask, request, session, render_template, redirect, url_for
from flask import _request_ctx_stack as stack
from random import randint
from jaeger_client import Tracer, ConstSampler
from jaeger_client.reporter import NullReporter
from jaeger_client.codecs import B3Codec
from opentracing.ext import tags
from opentracing.propagation import Format
from opentracing_instrumentation.request_context import get_current_span, span_in_context
import requests
import os

app = Flask(__name__)

# A very basic OpenTracing tracer (with null reporter)
tracer = Tracer(
    one_span_per_rpc=True,
    service_name='productpage',
    reporter=NullReporter(),
    sampler=ConstSampler(decision=True),
    extra_codecs={Format.HTTP_HEADERS: B3Codec()}
)


def trace():
    '''
    Function decorator that creates opentracing span from incoming b3 headers
    '''
    def decorator(f):
        def wrapper(*args, **kwargs):
            request = stack.top.request
            try:
                # Create a new span context, reading in values (traceid,
                # spanid, etc) from the incoming x-b3-*** headers.
                span_ctx = tracer.extract(
                    Format.HTTP_HEADERS,
                    dict(request.headers)
                )
                # Note: this tag means that the span will *not* be
                # a child span. It will use the incoming traceid and
                # spanid. We do this to propagate the headers verbatim.
                rpc_tag = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}
                span = tracer.start_span(
                    operation_name='op', child_of=span_ctx, tags=rpc_tag
                )
            except Exception as e:
                # We failed to create a context, possibly due to no
                # incoming x-b3-*** headers. Start a fresh span.
                # Note: This is a fallback only, and will create fresh headers,
                # not propagate headers.
                span = tracer.start_span('op')
            with span_in_context(span):
                r = f(*args, **kwargs)
                return r
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator


def getForwardHeaders(request):
    headers = {}

    # x-b3-*** headers can be populated using the opentracing span
    span = get_current_span()
    carrier = {}
    tracer.inject(
        span_context=span.context,
        format=Format.HTTP_HEADERS,
        carrier=carrier)

    headers.update(carrier)

    # We handle other (non x-b3-***) headers manually
    if 'user' in session:
        headers['end-user'] = session['user']

    incoming_headers = ['x-request-id', 'x-datadog-trace-id', 'x-datadog-parent-id', 'x-datadog-sampled']

    # Add user-agent to headers manually
    if 'user-agent' in request.headers:
        headers['user-agent'] = request.headers.get('user-agent')

    for ihdr in incoming_headers:
        val = request.headers.get(ihdr)
        if val is not None:
            headers[ihdr] = val
            # print "incoming: "+ihdr+":"+val

    return headers


@app.route("/")
@trace()
def route():
    count = request.args.get("count",  default = 0, type = int) # How far to iterate
    caller = request.args.get("caller",  default = 0, type = int) # How far to iterate
    identity = int(os.getenv("IDENTITY")) # Identity of the running service
    services = int(os.getenv("SERVICES")) # The amount of services running
    print(services)
    headers = getForwardHeaders(request)
    if count > services:
        return "Count cannot be greater than the amount of services"
    if count != 0: # End once the count reaches 0
        for x in range(identity+1, services+1): # Prevent circular calls
            print(x)
            if caller == x: # No callbacks to the original caller
                continue
            #if randint(0, 3) % 3 == 0: # Add some randomness to the demo
            url = "http://mesh-demo-{}:5000".format(x)
            print("Request to {} from service {}".format(url, identity))
            requests.get(url, params={'count': count-1, 'caller': identity}, headers=headers)
    return "SUCCESS"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True,host='0.0.0.0',port=port)