import tensorflow as tf
import numpy as np
import cv2


def __read_image(filename, resize_height, resize_width, normalization=False):
    """
    读取图片数据,默认返回的是uint8,[0,255]
    :param filename:
    :param resize_height:
    :param resize_width:
    :param normalization:是否归一化到[0.,1.0]
    :return: 返回的图片数据
    """
    bgr_image = cv2.imread(filename)
    if len(bgr_image.shape) == 2:  # 若是灰度图则转为三通道
        print("Warning:gray image", filename)
        bgr_image = cv2.cvtColor(bgr_image, cv2.COLOR_GRAY2BGR)

    rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)  # 将BGR转为RGB
    # show_image(filename,rgb_image)
    # rgb_image=Image.open(filename)
    if resize_height > 0 and resize_width > 0:
        rgb_image = cv2.resize(rgb_image, (resize_width, resize_height))
    rgb_image = np.asanyarray(rgb_image)
    if normalization:
        # 不能写成:rgb_image=rgb_image/255
        rgb_image = rgb_image / 255.0
    # show_image("src resize image",image)
    return rgb_image


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
            im = __read_image(image_path, 299, 299, normalization=True)
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
