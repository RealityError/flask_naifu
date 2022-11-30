import requests,base64
import hashlib
import logging

class webui_(object):
    '''
    定义画图初始类，其实并不需要全部内容生成json


    属性:
        高分辨率选项内容：
            enable_hr: bool 默认值 False 
            是否启用高分辨率修复，默认不启用
            denoising_strength:int 默认值  0
            降噪强度
            firstphase_width: int 默认值 0
            第一遍的高度
            firstphase_height: int 默认值 0
            第一遍的宽度
        图片生成内容:  
            prompt : str
            提示词
            negative_prompt: str
            反向提示词
            styles : str  默认值 None
            是否使用模板
            batch_size : int 默认值  1
            一次生成多少张图像
            n_iter : int 默认值 1   

            steps : int 默认值 28
            迭代步数
            cfg_scale: int 默认值 7
            自由度
            width : int 默认值 512
            图片高度
            height : int 默认值 512
            图片宽度
            seed : int 默认值 -1
            生成种子
            sampler_index : str 默认值 "Euler"
            采样方式

            imgimg参数：
            tips：这里没有启用蒙版的参数

            init_images  str 默认值 
            存储图片
            denoising_strength float 默认值 0.75
            强度
            include_init_images
            包含初始图  


            种子额外参数：


                subseed : int 默认值-1
                差异随机种子
                subseed_strength : int 默认值 0
                差异强度
                seed_resize_from_h : int 默认值 -1
                差异随机种子高度
                seed_resize_from_w : int 默认值 -1
                差异随机种子宽度



        restore_faces : bool 默认值 False
        面部修复
        tiling :bool 默认值 False
        生成平铺图像


        不知道干什么的数值:

        eta : int 默认值 0
        s_churn : int 默认值 0
        s_tmax : int 默认值0
        s_tmin : int 默认值0
        s_noise : int 默认值1


        override_settings: list 默认值 {}
        脚本的设定



    '''
    enable_hr: bool = False
    firstphase_width: int = 0
    firstphase_height: int = 0
    prompt: str
    styles: list = None
    seed: int = -1
    subseed: int = -1
    subseed_strength: int = 0
    seed_resize_from_h: int = -1
    seed_resize_from_w: int = -1
    batch_size: int = 1
    n_iter: int = 1
    steps: int = 28
    cfg_scale: float = 7
    width: int = 512
    height: int = 512
    restore_faces: bool = False
    tiling: bool = False
    negative_prompt: str = None
    eta: int = 0
    s_churn: int = 0
    s_tmax: int = 0
    s_tmin: int = 0
    s_noise: int = 1
    override_settings: list = []
    sampler_index: str = "Euler" 
    init_images: str = None
    denoising_strength: float = 0
    include_init_images: bool = False
    resize_mode : int = 0
    mask: str = "",
    mask_blur: int = 4,
    inpainting_fill:int = 0,
    inpaint_full_res: bool =   True,
    inpaint_full_res_padding:int = 0,
    inpainting_mask_invert: int =0,
    
    #从init.json中导入一些变量
    api_t2i:str = "",
    api_i2i:str = "",
    #request的json
    playload = {}
    n_samples:int = 0
    #初始化数据
    def __init__(self,img_data,data) -> None:
        #提示词
        self.prompt = img_data['prompt']  
        self.negative_prompt = img_data['uc']
        #图片大小
        self.width = img_data['width']  
        self.height = img_data['height']  
        
        self.cfg_scale = img_data['scale'] 
        self.steps = img_data['steps']   
        
        #图片数量
        self.n_samples = img_data["n_samples"]
        
        # TODO(me): 这里记得改采样方式对照表
        #img_data['sampler'] = self.sampler_index
        #生成数量：n_samples没有使用
        self.seed = img_data["seed"]  
        if img_data.has_key('strength'):
            self.denoising_strength = img_data['strength']
        if img_data.has_key('img') != None:
           self.init_images = img_data["image"]
        self.api_t2i = data["api_t2i"]
        self.api_i2i = data["api_i2i"]
        
    def text2img(self):
    
    #数据导入
        self.payload = {
        "prompt":self.prompt,
        "seed": self.seed,
        "steps": self.steps,
        "cfg_scale": self.cfg_scale,
        "width":  self.width,
        "height": self.height,
        "negative_prompt": self.negative_prompt,
        "sampler_index": self.sampler_index
        }
        
    def img2img(self):
    
        img_payload = {
                    "init_images": [
                        'data:image/png;base64,' + self.init_images
                    ],
                    "denoising_strength": self.denoising_strength
                }   
        self.payload = {
        "prompt":self.prompt,
        "seed": self.seed,
        "steps": self.steps,
        "cfg_scale": self.cfg_scale,
        "width":  self.width,
        "height": self.height,
        "negative_prompt": self.negative_prompt,
        "sampler_index": self.sampler_index
        }
        self.payload.update(img_payload)

        
    def generate(self,response,setting_data):
        #初始变量
        images_encoded = []
        data = ""
        ptr = 0
        #向本地webui端发送请求
        if self.init_images != None:
            api = self.api_i2i
            self.img2img()
        else:
            api = self.api_t2i
            self.text2img()
        # TODO(me): 这里记得写多网站队列（感觉用不上。
        
        
        #多图生成
        for i in range(self.n_samples):
            req = requests.post(url = setting_data["draw"]["webui"][0]+api,json=self.payload)
            if str(req) == "<Response [200]>":
                img_data = req.json()
                image = img_data['images'][0]
                image_s = base64.b64decode(image)   
                fmd5 = hashlib.md5(image_s).hexdigest()
                with open(r"output/"+str(fmd5)+ ".png", "wb") as fh:
                    fh.write(image_s)
                images_encoded.append(image)
        
        for x in images_encoded:
            ptr += 1
            data+= ("event: newImage\nid: {}\ndata:{}\n\n").format(ptr, x)
    
        response.data = data
        response.media_type = "text/event-stream"
        return response
    
    