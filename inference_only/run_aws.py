from automatic_annotation_pipeline import annotate
import os
from book_of_whales import make_book_of_whales
import boto3

dir_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Phase 2 predictions with a confidence above this threshold will be in the final output. Default value is 0.5.
prediction_th = 0.5 

# Windows with a phase 1 prediction confidence above this threshold will be passed to phase 2. Default value is 0.7.
sending_th = 0.7 

# Path to the checkpoint for the SoundNet model used in phase 1. Default value is "phase_1_checkpoints/phase_1_soundnet.pt".
path_to_phase_1_soundnet_checkpoint=os.path.join(dir_root, "phase_1_checkpoints/phase_1_soundnet.pt")

# Path to the checkpoint for the MLP model used in phase 1. Default value is "phase_1_checkpoints/phase_1_mlp.pt".
path_to_phase_1_mlp_checkpoint=os.path.join(dir_root, "phase_1_checkpoints/phase_1_mlp.pt")

# Path to the checkpoint for the SoundNet model used in phase 2. Default value is "phase_2_checkpointss/phase_2_soundnet.pt".
path_to_phase_2_soundnet_checkpoint=os.path.join(dir_root, "phase_2_checkpoints/phase_2_soundnet.pt")

# Path to the checkpoint for the transformer model used in phase 2. Default value is "phase_2_checkpoints/phase_2_transformer.pt".
path_to_phase_2_transformer_checkpoint=os.path.join(dir_root, "phase_2_checkpoints/phase_2_transformer.pt")

# Path to the checkpoint for the linear model used in phase 2. Default value is "phase_2_checkpoints/phase_2_linear.pt".
path_to_phase_2_linear_checkpoint=os.path.join(dir_root, "phase_2_checkpoints/phase_2_linear.pt")

# Path to the checkpoint for the coda model used in phase 2. Default value is "phase_2_checkpoints/phase_2_coda.pt".
path_to_phase_2_coda_checkpoint=os.path.join(dir_root, "phase_2_checkpoints/phase_2_coda.pt")

# Path to the checkpoint for the whale model used in phase 2. Default value is "phase_2_checkpoints/phase_2_whale.pt".
path_to_phase_2_whale_checkpoint=os.path.join(dir_root, "phase_2_checkpoints/phase_2_whale.pt")

# If you want an additional output file with all the candidate windows found by phase 1. Default value is False.
store_phase_1_predictions=False

# If you want an additional output file with the confidences of phase 1 for every window. Default value is False.
store_all_phase_1_confidences=False

# If you want an additional output file with the raw output of phase 2. Default value is False.
store_phase_2_output=False

# If you want to print phase 1 outputs as they are calculated. Default value is False.
print_p1_output = False

# If you want to print phase 2 outputs as they are calculated. Default value is False.
print_p2_output = False

s3 = boto3.client('s3', 
                  region_name="us-east-1", )
                #   endpoint_url="https://s3.us-east-1.amazonaws.com") # real, region is n. virginia where bucket is
# s3 = boto3.client('s3', endpoint_url="http://localhost:4566") # for non-docker local testing
# s3 = boto3.client('s3', endpoint_url="http://host.docker.internal:4566") # for docker local testing


if __name__ == "__main__":

    print('starting...')
    
    input_s3_bucket = os.environ["INPUT_S3_BUCKET"]
    input_s3_key = os.environ["INPUT_S3_KEY"]


    local_input_audio_file_name = "input.wav" # name for aws to load data into
    s3.download_file(input_s3_bucket, input_s3_key, local_input_audio_file_name) # puts file into root

    parsed = input_s3_key.split('/')
    prefix = '/'.join(parsed[:-1]) + '/' # note: will need to add a line to after this.
    true_filename = parsed[-1].replace('.wav', '')
    target_prefix = prefix.replace('raw', 'martin_annotated') # WE EXPECT TO BE IN RAW/
    if target_prefix == '/': # edge case where there is no prefix
        target_prefix = ''
    print(f'{target_prefix=}')
    print(f'{true_filename=}')


    annotation_output_path = os.path.join(dir_root, f"{true_filename}_aws_annotations.csv")
    book_of_whales_output_path = os.path.join(dir_root, f"{true_filename}_aws_book_of_whales.pdf")


    print('running annotate...')

    annotate(   input_file=local_input_audio_file_name,
                output_file=annotation_output_path,
                prediction_th=prediction_th,
                sending_th=sending_th,
                path_to_phase_1_soundnet_checkpoint=path_to_phase_1_soundnet_checkpoint,
                path_to_phase_1_mlp_checkpoint=path_to_phase_1_mlp_checkpoint,
                path_to_phase_2_soundnet_checkpoint=path_to_phase_2_soundnet_checkpoint,
                path_to_phase_2_transformer_checkpoint=path_to_phase_2_transformer_checkpoint,
                path_to_phase_2_linear_checkpoint=path_to_phase_2_linear_checkpoint,
                path_to_phase_2_coda_checkpoint=path_to_phase_2_coda_checkpoint,
                path_to_phase_2_whale_checkpoint=path_to_phase_2_whale_checkpoint,
                store_phase_1_predictions=store_phase_1_predictions,
                store_all_phase_1_confidences=store_all_phase_1_confidences,
                store_phase_2_output=store_phase_2_output,
                print_p1_output=print_p1_output,
                print_p2_output=print_p2_output)
    
    print('running book of whales...')


    make_book_of_whales(annotation_output_path, book_of_whales_output_path)


    s3.upload_file(annotation_output_path, input_s3_bucket, os.path.join(target_prefix, f"{true_filename}_annotations.csv"))
    print('uploaded annotations.')
    try:
        s3.upload_file(book_of_whales_output_path, input_s3_bucket, os.path.join(target_prefix, f"{true_filename}_book_of_whales.pdf"))
        print('uploaded book of whales.')
    except FileNotFoundError:
        print(f'no book of whales made, skipping.')
    print('finished.')