import os, json

path_to_json = 'C:/Users/choco/Downloads/CVR_Export/votes/'
vote_data = {}

def readFiles():
    for file in os.listdir(path_to_json):
        f = open(path_to_json + file)
        file_data = json.load(f)
        f.close()
        
        for session in file_data["Sessions"]:
            for card in session["Original"]["Cards"]:
                for contest in card["Contests"]:
                    contest_id = contest["Id"]
                    if contest_id not in vote_data:
                        vote_data[contest_id] = []
                    my_ballot = []
                    prev_rank = 0
                    for mark in contest["Marks"]:
                        my_ballot.append(mark["CandidateId"])
                        prev_rank = mark["Rank"]
                    vote_data[contest_id].append(my_ballot)
        print("Completed file " + str(file))

def calcPairs(contestIndex):
    contest = vote_data[contestIndex]
    candidateList = []
    for ballot in contest:
        for vote in ballot:
            if vote not in candidateList:
                candidateList.append(vote)
    print(candidateList)
                
    results = {}
    for c1 in candidateList:
        results[c1] = {}
        for c2 in candidateList:
            results[c1][c2] = 0

    for ballot in contest:
        pending = candidateList.copy()
        for vote in ballot:
            if vote not in pending:
                break
            pending.remove(vote)
            for c in pending:
                results[vote][c] += 1

    return results
            
    
                
