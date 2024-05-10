class Worker:
    def h():
        pass


class Medium:
    a : Worker
    b : Worker
    
    
    def botify(self , other):
        for i in self.a , self.b:
            if i is not other:
                i.h()


    def register(self, w : Worker):