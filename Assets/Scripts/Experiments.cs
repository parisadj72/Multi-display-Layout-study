using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

public class Experiments : MonoBehaviour
{
    public List<TaskManagement> layouts = new List<TaskManagement>();
    private TaskManagement currentLayout;

    private List<int> randomLayouts = new List<int>();

    private int instantiatedLayout;

    private float timer;
    float sumOfNumberOfWorngSelections;
    public string timerFilePath;

    public enum Experiment { Exp1, Exp2, Exp3 };
    public Experiment experiment;

    public enum StudyNumber { Study1, Study2 };
    public StudyNumber studyNumber;

    private void Awake()
    {
        randomLayouts = RandomGenerator.generateUniqueRandoms(layouts.Count, 3);
    }
    private void Start()
    {
        createOutputFile();
        StartCoroutine(WaitForTask());
    }

    IEnumerator WaitForTask()
    {
        print("Task in progress");

        for (int i = 0; i < randomLayouts.Count; i++)
        {
            //start timer
            timer = 0;
            //count errors
            sumOfNumberOfWorngSelections = 0;

            instantiatedLayout = randomLayouts[i];

            Instantiate(layouts[instantiatedLayout], transform);

            currentLayout = GetComponentInChildren<TaskManagement>();
            currentLayout.NumberOfSwaps = 0;

            yield return new WaitUntil(() => currentLayout.TaskDone);

            //Log time per trial in the file
            if(experiment == Experiment.Exp1)
                File.AppendAllText(timerFilePath, "(time per " + currentLayout.task1Selections + " Selections for the " + currentLayout.layoutName + " layout): " + timer + "\n \n");
            else if (experiment == Experiment.Exp2)
                File.AppendAllText(timerFilePath, "(time per " + currentLayout.selections + " Selections for the " + currentLayout.layoutName + " layout): " + timer + "\n \n");
            else if (experiment == Experiment.Exp3)
                File.AppendAllText(timerFilePath, "Trial time (# " + currentLayout.NumberOfSwaps + " swaps for the " + currentLayout.layoutName + " layout): " + timer + "\n \n");

            //log Error: Wrong Selections
            for (int k = 0; k < currentLayout.Views.Count; k++)
            {
                sumOfNumberOfWorngSelections += currentLayout.Views[k].WrongClickCounter;
            }
            if (experiment == Experiment.Exp1)
                File.AppendAllText(timerFilePath, "(Errors / Wrong Selections per " + currentLayout.task1Selections + " Selections for the " + currentLayout.layoutName + " layout): " + sumOfNumberOfWorngSelections + "\n \n");
            else if (experiment == Experiment.Exp2)
                File.AppendAllText(timerFilePath, "(Errors / Wrong Selections per " + currentLayout.selections + " Selections for the " + currentLayout.layoutName + " layout): " + sumOfNumberOfWorngSelections + "\n \n");
            else if (experiment == Experiment.Exp3)
                File.AppendAllText(timerFilePath, "Errors per trial for the " + currentLayout.layoutName + " layout: " + sumOfNumberOfWorngSelections + "\n \n");

            if (experiment == Experiment.Exp3)
            {
                Destroy(currentLayout.gameObject);
                GameObject[] remainingViews = GameObject.FindGameObjectsWithTag("View");

                foreach (GameObject go in remainingViews)
                {
                    Destroy(go);
                }
                yield return new WaitForSeconds(1);

            } else {
                Destroy(currentLayout.gameObject, 5);
                yield return new WaitForSeconds(5);

            }
        }
    }
    private void createOutputFile()
    {
        int subjectID = 1;
        timerFilePath = "Assets/OutputLog/"+ studyNumber +"subject" + subjectID + experiment + ".txt";
        while (File.Exists(timerFilePath))
        {
            subjectID++;
            timerFilePath = "Assets/OutputLog/" + studyNumber + "subject" + subjectID + experiment + ".txt";
        }
        File.WriteAllText(timerFilePath, "OUTPUT OF EACH RUN (" + experiment + "): \n \n");
    }

    private void LayoutInfo()
    {
        print(instantiatedLayout);
        print(layouts[instantiatedLayout].isActiveAndEnabled);
    }

    private void Update()
    {
        timer += Time.deltaTime;
        if (Input.GetKey(KeyCode.I))
        {
            LayoutInfo();
        }
    }
}
