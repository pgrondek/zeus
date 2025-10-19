
import os
from stv.stv import count_stv, Ballot
import io
import logging

from zeus.results_report import build_stv_doc
from datetime import datetime


def stv_count_and_report(uuid, el_data, base_path="/tmp/"):
    eligibles = el_data['numOfEligibles']
    elected_limit = el_data['electedLimit']
    ballots = el_data['ballots']
    input_ballots = []
    elName = el_data.get("elName")
    pollName = el_data.get("pollName", elName)
    institution = el_data.get("institution", "")
    voting_starts = el_data.get("votingStarts", datetime.now())
    voting_ends = el_data.get("votingEnds", datetime.now())
    if isinstance(voting_starts, str):
        voting_starts = datetime.strptime(voting_starts, "%d/%m/%Y %H:%M")
    if isinstance(voting_ends, str):
        voting_ends = datetime.strptime(voting_ends, "%d/%m/%Y %H:%M")

    constituencies = {}
    schools = el_data['schools']
    answers = {}
    answers_list = []

    for item in schools:
        school_name = item['Name']
        for candidate in item['candidates']:
            candId = "{} {}:{}".format(candidate['firstName'],
                                            candidate['lastName'],
                                            school_name)
            answers[str(candidate['candidateTmpId'])] = candId
            answers_list.append(candId)
            constituencies[str(len(answers_list)-1)] = school_name

    for ballot in ballots:
        orderedCandidateList = []
        for rank in range(1, len(ballot['votes'])+1):
            for vote in ballot['votes']:
                if vote['rank'] == rank:
                    candId = vote['candidateTmpId']
                    candName = answers[str(candId)]
                    index = str(answers_list.index(candName))
                    orderedCandidateList.append(index)
        input_ballots.append(Ballot(orderedCandidateList))

    stv_stream = io.StringIO()
    stv_logger = logging.Logger("stv-poll")
    handler = logging.StreamHandler(stv_stream)
    stv_logger.addHandler(handler)
    stv_logger.setLevel(logging.DEBUG)

    count_results = count_stv(input_ballots, eligibles,
                                droop=True,
                                constituencies=constituencies,
                                quota_limit=elected_limit if elected_limit else 0,
                                rnd_gen=None, logger=stv_logger)

    results = list(count_results[0:2])
    voters = list(range(len(ballots)))

    questions = [{'tally_type': 'stv', 'choice_type': 'stv',
                    'question': 'Questions choices', 'answers':
                    answers_list, 'answer_urls': [None, None],
                    'result_type': 'absolute'}]

    handler.close()
    stv_stream.seek(0)
    results.append(stv_stream.read())

    poll_name, poll_results, questions, poll_voters = \
        pollName, results, questions, voters

    class Voters(list):
        def count(self):
            return len(self)

        def excluded(self):
            return Voters()

    filename = os.path.join(base_path, "stv-results-{}.pdf".format(uuid))
    poll_voters = Voters(poll_voters)
    data = [[poll_name, poll_results, questions, poll_voters]]
    build_stv_doc(elName, pollName, institution, voting_starts,
                    voting_ends, None, data, 'el',
                    filename=filename)
    return [('pdf', filename)]
