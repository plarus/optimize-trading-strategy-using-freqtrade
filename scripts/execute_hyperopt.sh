#!/bin/bash
# Execute hyperopt with different configuration and extract all results in a CSV file

allTimeframe=("5m" "15m" "1h" "1d")

allLossFunctions=("ShortTradeDurHyperOptLoss" "OnlyProfitHyperOptLoss" "SharpeHyperOptLoss" "SharpeHyperOptLossDaily" "SortinoHyperOptLoss" "SortinoHyperOptLossDaily")

allStrategy=("BBRSINaiveStrategyWithHyperoptCode")

numberOfEpochs="100"

for strategy in "${allStrategy[@]}"; do
    for lossFunction in "${allLossFunctions[@]}"; do
        for timeframe in "${allTimeframe[@]}"; do
            echo "$strategy $lossFunction $timeframe"
            sudo docker-compose run --rm freqtrade hyperopt --print-json --hyperopt-loss $lossFunction --strategy $strategy -i $timeframe -e $numberOfEpochs > tmp.log
            ./extract_hyperopt_result.py -i tmp.log -l $lossFunction -s $strategy -t $timeframe
        done
    done
done
