def my_function(x, output_queue):
    output_queue.put((x, x * 10))
    
def my_function_ml_procs(num, conn):
    try:
        # Do some computation
        result = {"input": num, "output": num * 2}  # Example
        conn.send(result)
    except Exception as e:
        conn.send({"error": str(e)})
    finally:
        conn.close()