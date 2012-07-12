import logging
import time
import traceback
import socket
import sys

import twittersense.aws.sqs as sqs


def read(queue_name, processor, sleep_time, delete_on_except=False,
         message_type=None):
    """Process messages on the queue.

        :param processor: Function used to process one message. The function
            should return True if the message is to be deleted from the
            queue after processing, False otherwise.
        :param queue_name: The SQS queue name.
        :param sleep_time: Queue polling time, in seconds.
        :param delete_on_except: Whether or not to delete a message when an
            exception is raised, default: false.
        :param message_type: A message's class. An instance of that class
            will be created when extracting a message from the queue.
    """
    queue = sqs.get(queue_name)
    if message_type:
        queue.set_message_class(message_type)
    logging.info("Ready. Listening on queue {!r}.".format(queue_name))
    while True:
        try:
            message = queue.read()
        except Exception, exception:
            logging.critical("Exception: {!r}".format(exception))
        else:
            if message is None:
                # Sleep if no message.
                time.sleep(sleep_time)
            else:
                try:
                    # Process message.
                    if processor(message):
                        queue.delete_message(message)

                except socket.error, exception:
                    logging.error("Socket exception: {!r}".format(exception))
                    logging.debug(traceback.format_exc())
                    if message and delete_on_except:
                        queue.delete_message(message)
                except Exception, exception:
                    logging.error(str(exception))
                    logging.debug(traceback.format_exc())
                    if message and delete_on_except:
                        queue.delete_message(message)
                except (KeyboardInterrupt, SystemExit):
                    break
                except:
                    logging.critical("Unknown exception.")
                    logging.info(traceback.format_exc())
                    if message and delete_on_except:
                        queue.delete_message(message)


def reader_writer(message):
    sys.stderr.write(message.get_body() + "\n")
    return True


if __name__ == '__main__':
    if len(sys.argv) > 1:
        queue_name = sys.argv[1]
    else:
        sys.exit("Please provide a queue name.")
    print("Reading messages from queue {!r}:\n\n".format(queue_name))
    read(queue_name, reader_writer, 2)
