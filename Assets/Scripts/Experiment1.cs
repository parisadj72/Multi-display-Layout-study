using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

public class Experiment1 : MonoBehaviour
{
    public List<SelectionTask> layouts = new List<SelectionTask>();
    private List<int> randomLayouts = new List<int>();
    private int instantiatedLayout;
    private SelectionTask currentLayout;
    private float timer;
    float sumOfNumberOfWorngSelections;
    private string timerFilePath;

    public enum Experiment { Exp1, Exp2, Exp3 };
    public Experiment experiment;

    private void Awake()
    {
        randomLayouts = RandomGenerator.randomizeList(layouts.Count);
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

            currentLayout = GetComponentInChildren<SelectionTask>();

            yield return new WaitUntil(() => currentLayout.TaskDone);

            //Log time per trial in the file
            File.AppendAllText(timerFilePath, "(time per " + currentLayout.selections + " Selections): " + timer + "\n \n");

            print(currentLayout.name);
            Destroy(currentLayout.gameObject, 5);

            //log Error: Wrong Selections
            File.AppendAllText(timerFilePath, "\n \n OUTPUT OF EACH RUN (Errors): \n");
            File.AppendAllText(timerFilePath, "Number Of Wrong Selections = " + sumOfNumberOfWorngSelections + "\n \n");

            yield return new WaitForSeconds(5);
            //StartCoroutine(TakeBreak(5));
        }
    }
    private void createOutputFile()
    {
        int subjectID = 1;
        timerFilePath = "Assets/OutputLog/subject" + subjectID + experiment + ".txt";
        while (File.Exists(timerFilePath))
        {
            subjectID++;
            timerFilePath = "Assets/OutputLog/subject" + subjectID + experiment + ".txt";
        }
        File.WriteAllText(timerFilePath, "OUTPUT OF EACH RUN (" + experiment + "): \n \n");
    }

    IEnumerator TakeBreak(int time)
    {
        //Learned something new today: Calling a coroutine to stop the 
        // execution of another one does not work. 
        // What stops is the coroutine you call. Not the calling coroutine
        yield return new WaitForSeconds(time);
    }

    private void LayoutInfo()
    {
        print(instantiatedLayout);
        print(layouts[instantiatedLayout].isActiveAndEnabled);
    }

    private void Update()
    {
        timer += Time.deltaTime;
        for (int k = 0; k < currentLayout.Views.Count; k++)
        {
            sumOfNumberOfWorngSelections += currentLayout.Views[k].WrongClickCounter;
        }
        if (Input.GetKey(KeyCode.I))
        {
            LayoutInfo();
        }
    }

    private void TraverseList(List<SelectionTask> list)
    {
        foreach (SelectionTask selT in list)
        {
            print(selT.name);
        }
    }

    private void TraverseList(List<int> list)
    {
        foreach (int selT in list)
        {
            print(selT);
        }
    }
}
