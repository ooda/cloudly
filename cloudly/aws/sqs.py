import logging
import time
import traceback
import socket
import sys

import boto
import boto.sqs.message

Message = boto.sqs.message.Message

SQS_MAXIMUM_MESSAGE_SIZE = 65536
SQS_TIMEOUT = 60


def write(queue, message):
    if(len(message) > SQS_MAXIMUM_MESSAGE_SIZE):
        raise Exception(
            "Can't queue to {!r}, size {} greater than {} bytes.".format(
                queue.name, len(message), SQS_MAXIMUM_MESSAGE_SIZE))

    status = queue.write(message)
    if not status:
        raise Exception("Could not write to SQS queue {!r}".format(queue.name))


def get(queue_name, do_create=True):
    # Initialize the connection to SQS.
    connection = boto.connect_sqs()
    # Create an AWS SQS queue if it does not exists or retrieve it if it does
    # exists.
    queue = connection.get_queue(queue_name)
    if not queue and do_create:
        queue = create(queue_name)
    elif not queue:
        raise Exception("Could not get queue '" + queue_name + "'")
    return queue


def create(queue_name):
    # Connect to the AWS SQS service and create a queue if it does not exists
    # yet.
    connection = boto.connect_sqs()
    sqs_queue = connection.create_queue(queue_name, SQS_TIMEOUT)
    if not sqs_queue.set_attribute("MaximumMessageSize",
                                  SQS_MAXIMUM_MESSAGE_SIZE):
        raise Exception(
            "Can't set MaximumMessageSize to {} bytes for {!r}.".format(
                SQS_MAXIMUM_MESSAGE_SIZE, queue_name))
    if not sqs_queue:
        raise Exception("Could not create queue {!r}".format(queue_name))
    return sqs_queue


def count(queue_name):
    queue = get(queue_name, False)
    return queue.count()


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
    queue = get(queue_name)
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
