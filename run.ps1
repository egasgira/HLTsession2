$BASEDIR="../labAHLT"

# conda
# C:/Users/morit/anaconda3/Scripts/activate
#conda activate ahlt

# convert datasets to feature vectors
Write-Output "Extracting features..."
python extract-features.py "$BASEDIR/data/train/" > train.feat
python extract-features.py "$BASEDIR/data/devel/" > devel.feat

# train CRF model
Write-Output "Training CRF model..."
Get-Content train.feat | python train-crf.py model.crf
# run CRF model
Write-Output "Running CRF model..."
Get-Content devel.feat | python predict.py model.crf devel-CRF.out
# evaluate CRF results
Write-Output "Evaluating CRF results..."
python "$BASEDIR/evaluator.py" NER "$BASEDIR/data/devel" devel-CRF.out > devel-CRF.stats

# train MEM model
Write-Output "Training MEM model..."
(Get-Content train.feat | ForEach-Object { $_.Split()[4..($_.Split().Count-1)] -join "`t" } | Out-String).Trim() | Out-File train.mem.feat
./megam-64.opt -nobias -nc -repeat 4 multiclass train.mem.feat > model.mem
Remove-Item train.mem.feat
# run MEM model
Write-Output "Running MEM model..."
Get-Content devel.feat | python predict.py model.mem devel-MEM.out
# evaluate MEM results
Write-Output "Evaluating MEM results..."
python "$BASEDIR/evaluator.py" NER "$BASEDIR/data/devel" devel-MEM.out > devel-MEM.stats