using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

public class Experiment1 : MonoBehaviour
{
    public List<SelectionTask> layouts = new List<SelectionTask>();
    private SelectionTask currentLayout;
    private SelectionTask layoutCopy;

    private List<int> randomLayouts = new List<int>();

    private int instantiatedLayout;

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

            if (experiment == Experiment.Exp3)
            {
                CopyAndDisplace(currentLayout);
            }

            yield return new WaitUntil(() => currentLayout.TaskDone);

            //Log time per trial in the file
            File.AppendAllText(timerFilePath, "(time per " + currentLayout.selections + " Selections): " + timer + "\n \n");

            //log Error: Wrong Selections
            for (int k = 0; k < currentLayout.Views.Count; k++)
            {
                sumOfNumberOfWorngSelections += currentLayout.Views[k].WrongClickCounter;
            }
            File.AppendAllText(timerFilePath, "(Errors / Wrong Selections per " + currentLayout.selections + " Selections): " + sumOfNumberOfWorngSelections + "\n \n");


            print(currentLayout.name);
            Destroy(currentLayout.gameObject, 5);

            
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
        if (Input.GetKey(KeyCode.I))
        {
            LayoutInfo();
        }
    }

    private void CopyAndDisplace(SelectionTask original)
    {
        layoutCopy = original;

        switch (layoutCopy.NumberOfWindows)
        {
            case 3:
                print("3 views");
                if (layoutCopy.gameObject.tag == "Stack")
                {
                    print("got stack");
                    // Move to the right
                    Instantiate(layoutCopy, transform);
                    layoutCopy.Textures = original.Textures;
                }
                else
                {
                    // Move up
                    Instantiate(layoutCopy, transform);

                }
                break;
            case 6:
                print("6 views");
                Instantiate(layoutCopy, transform);
                break;
            case 12:
                print("12 views");
                Instantiate(layoutCopy, transform);
                break;
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
