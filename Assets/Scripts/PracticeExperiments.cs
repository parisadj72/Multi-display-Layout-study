using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PracticeExperiments : MonoBehaviour
{

    public List<PracticeTaskManagement> layouts = new List<PracticeTaskManagement>();
    private PracticeTaskManagement currentLayout;

    private List<int> randomLayouts = new List<int>();

    private int instantiatedLayout;

    public enum Experiment { Exp1, Exp2, Exp3 };
    public Experiment experiment;

    private void Awake()
    {
        randomLayouts = RandomGenerator.generateUniqueRandoms(layouts.Count, 1);
    }
    private void Start()
    {
        StartCoroutine(WaitForTask());
    }

    IEnumerator WaitForTask()
    {
        print("Task in progress");

        for (int i = 0; i < randomLayouts.Count; i++)
        {

            instantiatedLayout = randomLayouts[i];

            Instantiate(layouts[instantiatedLayout], transform);

            currentLayout = GetComponentInChildren<PracticeTaskManagement>();

            yield return new WaitUntil(() => currentLayout.TaskDone);

            Destroy(currentLayout.gameObject, 5);

            if (experiment == Experiment.Exp3)
            {
                GameObject[] remainingViews = GameObject.FindGameObjectsWithTag("View");

                foreach (GameObject go in remainingViews)
                {
                    Destroy(go, 5);
                }
            }
            yield return new WaitForSeconds(5);
        }
    }
}
