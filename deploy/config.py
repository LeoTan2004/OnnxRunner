config = {
    # 0是摄像头，当然也可以是视频文件路径
    'video_path': 0,
    # 保存视频的路径
    'save_path': './save_video/video.avi',
    # 特征提取器的特征差值，（0-255）越小表示对于图像变化的敏感度越高
    'difference_feature_extractor': 5,
    # 唯一标识生成器，默认是时间戳，也可以是create_time_idauto_incr_id表示自定义增长值
    'id_generator': 'create_time_id',
    # 物体存储路径
    'object_repository_path': './data/data',
    # 检测器池的大小，这个参数决定了多少的进程并行计算，在开发环境（8核16线程CPU）环境下测试2个进程交替执行最佳
    'multi_detector_pool_size': 2,
}
