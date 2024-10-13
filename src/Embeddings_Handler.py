from src.Embeddings_utils.transE import  TransE_Handler

if __name__ == '__main__':
    transE_Handler = TransE_Handler()
    transE_Handler.train_model()
    transE_Handler.predict(trainig_results=transE_Handler.result)