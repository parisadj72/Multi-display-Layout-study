using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

public class MemoryTaskExperiment2 : MonoBehaviour
{
    public int numberOfRepeatPerLayout = 3;
    private float timePerTrial;
    string timerFilePath = "Assets/Scripts/Experiment2/OutputTimerLog/Exp2timer.txt";
    private void createFile(string filePathName)
    {
        if (File.Exists(filePathName))
        {
            //add a heading inside the .txt file
            File.WriteAllText(filePathName, "OUTPUT OF EACH RUN (Time): \n \n");
        }
    }
    private List<int> generateUniqueRandoms(int size, int repeat)
    {
        List<int> list = new List<int>(new int[size * repeat]);
        List<int> countList = new List<int>(new int[size]);

        for (int j = 0; j < size * repeat; j++)
        {
            int Rand = Random.Range(0, size);

            while (list.Contains(Rand) && countList[Rand] >= repeat)
            {
                Rand = Random.Range(0, size);
            }

            list[j] = Rand;
            countList[Rand]++;
        }
        return list;
    }
    // Start is called before the first frame update
    void Start()
    {
        //create the output file per run/participant
        createFile(timerFilePath);

        StartCoroutine(waiter());
    }
    IEnumerator waiter()
    {
        List<int> list = generateUniqueRandoms(gameObject.transform.childCount, numberOfRepeatPerLayout);

        for (int i = 0; i < list.Count; i++)
        {
            GameObject layout = gameObject.transform.GetChild(list[i]).gameObject;
            layout.transform.position = new Vector3(0.0f, 0.8f, 0.0f);
            layout.SetActive(true);

            List<ViewScript> views = new List<ViewScript>();            
            Transform[] ViewsTransforms = layout.GetComponentsInChildren<Transform>();
            foreach (Transform childTransform in ViewsTransforms)
            {
                ViewScript view = childTransform.GetComponent<ViewScript>();

                if (view != null)
                {
                    view.TurnOff();
                    view.DisableInteraction();
                    views.Add(view);
                }
            }
            int numberOfWindows = views.Count;

            if (numberOfWindows == 3)
            {
                //start timer -> timePerTrial
                timePerTrial = 0;

                List<int> rand2 = generateUniqueRandoms(3, 1); // random order
                for (int j = 0; j < 2; j++) // turn on 2 random views
                    views[rand2[j]].TurnOn();

                yield return new WaitForSeconds(5);

                for (int j = 0; j < 2; j++) // turn off the 2 views and enable interaction
                {
                    views[rand2[j]].TurnOff();
                    views[rand2[j]].EnableInteraction();
                }

                yield return new WaitUntil(() => views[rand2[0]].IsOn && views[rand2[1]].IsOn);

                //finish timer -> timePerTrial -> write time to the file
                File.AppendAllText(timerFilePath, "timePerTrial (2 Selections): " + timePerTrial + "\n");

                for (int j = 0; j < 2; j++) 
                    views[rand2[j]].DisableInteraction();
            }
            else if (numberOfWindows == 6)
            {
                //start timer -> timePerTrial
                timePerTrial = 0;

                List<int> rand3 = generateUniqueRandoms(6, 1);
                for (int j = 0; j < 3; j++) // turn on 3 random views
                    views[rand3[j]].TurnOn();

                yield return new WaitForSeconds(5);

                for (int j = 0; j < 3; j++) // turn off the 3 views
                {
                    views[rand3[j]].TurnOff();
                    views[rand3[j]].EnableInteraction();
                }
                
                yield return new WaitUntil(() => views[rand3[0]].IsOn && views[rand3[1]].IsOn && views[rand3[2]].IsOn);

                //finish timer -> timePerTrial -> write time to the file
                File.AppendAllText(timerFilePath, "timePerTrial (3 Selections): " + timePerTrial + "\n");

                for (int j = 0; j < 3; j++) // turn on 3 random views
                    views[rand3[j]].DisableInteraction();
            }
            else // numberOfWindows == 12
            {
                //start timer -> timePerTrial
                timePerTrial = 0;

                List<int> rand5 = generateUniqueRandoms(12, 1);
                for (int j = 0; j < 5; j++) // turn on 5 random views
                    views[rand5[j]].TurnOn();

                yield return new WaitForSeconds(5);

                for (int j = 0; j < 5; j++) // turn off the 5 views
                { 
                    views[rand5[j]].TurnOff();
                    views[rand5[j]].EnableInteraction();
                }
                
                yield return new WaitUntil(() => views[rand5[0]].IsOn && views[rand5[1]].IsOn && views[rand5[2]].IsOn && views[rand5[3]].IsOn && views[rand5[4]].IsOn);

                //finish timer -> timePerTrial -> write time to the file
                File.AppendAllText(timerFilePath, "timePerTrial (5 Selections): " + timePerTrial + "\n");

                for (int j = 0; j < 5; j++) 
                    views[rand5[j]].DisableInteraction();
            }

            yield return new WaitForSeconds(5);
            layout.SetActive(false);

        }
    }

    // Update is called once per frame
    void Update()
    {
        timePerTrial += Time.deltaTime;
    }
}
