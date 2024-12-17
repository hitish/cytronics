from gliner import GLiNER

class XomadGliner:

    def __init__(self, models=1, use_gpu=False):
        
        if use_gpu:
            device= "cuda:0"
        else:
            device = "cpu"
        batch_size = 1    
        #self.scorer = LMScorer.from_pretrained("gpt2", device=device, batch_size=batch_size)    
        self.device = device
        self.model_loaded = False

    
        self.model = GLiNER.from_pretrained("xomad/gliner-model-merge-large-v1.0")
        self.model  = self.model.to(device)
        self.model_loaded = True
        print("Xomad Gliner model loaded...")
    

    def detect(self, text,labels):
      #print("in correction model")
      if self.model_loaded:
        entities = self.model.predict_entities(text, labels)

        for entity in entities:
            print(entity["text"], "=>", entity["label"])
        
        return entities
       
      else:
        print("Model is not loaded")  
        return None