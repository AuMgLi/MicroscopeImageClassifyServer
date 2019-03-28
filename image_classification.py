import tensorflow as tf
import numpy as np
from PIL import Image


def __preprocess_image(image_path):
    src_img = Image.open(image_path)
    # print('src_image mode is:', src_img.mode)
    width, height = src_img.size
    if width > height:
        diff = (width - height) // 2
        cropped = src_img.crop((diff, 0, width - diff, height))
    else:
        diff = (height - width) // 2
        cropped = src_img.crop((0, diff, width, height - diff))
    cropped = cropped.resize((299, 299), Image.ANTIALIAS)
    return cropped


def __read_image(image_path, normalization=True):
    image = __preprocess_image(image_path)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image = np.asanyarray(image)
    if normalization:
        image = image / 255.0
    # show_image("src resize image",image)
    return image


def do_classification(image_path):
    pb_path = 'model/frozen_model_14400_0.9878.pb'
    with tf.Graph().as_default():
        output_graph_def = tf.GraphDef()
        with open(pb_path, "rb") as f:
            output_graph_def.ParseFromString(f.read())
            tf.import_graph_def(output_graph_def, name="")
        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())

            # 定义输入的张量名称,对应网络结构的输入张量
            # input:0作为输入图像,keep_prob:0作为dropout的参数,测试时值为1,is_training:0训练参数
            input_image_tensor = sess.graph.get_tensor_by_name("input:0")
            input_keep_prob_tensor = sess.graph.get_tensor_by_name("keep_prob:0")
            input_is_training_tensor = sess.graph.get_tensor_by_name("is_training:0")

            # 定义输出的张量名称
            output_tensor_name = sess.graph.get_tensor_by_name("InceptionV3/Logits/SpatialSqueeze:0")

            # 读取测试图片
            im = __read_image(image_path, normalization=True)
            # print(im)
            # print(im.shape)
            im = im[np.newaxis, :]
            # 测试读出来的模型是否正确，注意这里传入的是输出和输入节点的tensor的名字，不是操作节点的名字
            out = sess.run(output_tensor_name, feed_dict={input_image_tensor: im,
                                                          input_keep_prob_tensor: 1.0,
                                                          input_is_training_tensor: False})
            print("out:{}".format(out))
            score = tf.nn.softmax(out, name='pred')
            class_id = tf.argmax(score, 1)
            # print("pred class_id:{}".format(sess.run(class_id)))
            return sess.run(class_id)[0]


if __name__ == '__main__':
    print(do_classification('image/35995.jpg'))
