- [ ] "If your goal is specifically to predict the winner out of a set, consider a 
 GroupedClassifier or a Ranker (like XGBRanker from the XGBoost library).
 These models are specifically designed to look at a group (the match) 
 and learn that one item in the group is better than the others, 
 rather than treating them as isolated data points."
- [ ] currently the predictor is dependent on some attributes from preprocessor, 
 as we only have one preprocessor available its not currently a problem but it may be
 Solution: have a preprocessor abstraction
- [ ] We may need a abstract predictor too on later stages of this project 
