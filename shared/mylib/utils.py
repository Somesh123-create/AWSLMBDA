def my_function(x, output_queue):
    output_queue.put((x, x * 10))