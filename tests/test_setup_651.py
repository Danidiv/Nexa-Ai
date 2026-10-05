from services.completion_repair_candidate_ranking import build_repair_candidate_ranking, valid_repair_candidate_ranking, RepairCandidateRanking

def main():
    print("============================================================")
    print("AZIZ AI SETUP 6.51 TEST")
    print("============================================================")
    obj=build_repair_candidate_ranking("sample", ["input-a", "input-b"], ["output-a"], ["evidence-a"])
    assert valid_repair_candidate_ranking(obj); print("[PASS] repair candidate ranking built")
    assert obj.inputs and obj.outputs and obj.evidence; print("[PASS] contract data preserved")
    assert valid_repair_candidate_ranking(obj); print("[PASS] digest validates")
    tampered=RepairCandidateRanking("tampered", obj.inputs, obj.outputs, obj.evidence, obj.digest)
    assert not valid_repair_candidate_ranking(tampered); print("[PASS] tamper rejected")
    print("Setup 6.51 tests complete.")

if __name__ == "__main__": main()
