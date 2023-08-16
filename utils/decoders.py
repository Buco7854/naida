async def read_stream_as_string(stream):
    output_string = ""

    while True:
        message = await stream.read_out()
        if message is None:
            break

        output_chunk = message.data.decode('utf-8')
        output_string += output_chunk

    return output_string
