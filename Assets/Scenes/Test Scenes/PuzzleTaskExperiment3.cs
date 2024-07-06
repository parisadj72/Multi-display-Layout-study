using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEngine.UI;

public class PuzzleTaskExperiment3 : MonoBehaviour
{
    public int numberOfRepeatPerLayout = 3;
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
        StartCoroutine(waiter());
    }
    IEnumerator waiter()
    {
        List<int> list = generateUniqueRandoms(gameObject.transform.childCount, numberOfRepeatPerLayout);

        for (int i = 0; i < list.Count; i++)
        {
            GameObject layout = gameObject.transform.GetChild(list[i]).gameObject;
            layout.transform.position = new Vector3(1.5f, 0.8f, 0.0f);
            layout.SetActive(true);

            List<ViewScript> views = new List<ViewScript>();
            List<ViewScript> puzzleViews = new List<ViewScript>();

            Transform[] ViewsTransforms = layout.GetComponentsInChildren<Transform>();
            foreach (Transform childTransform in ViewsTransforms)
            {
                if (childTransform.tag == "View")
                {
                    ViewScript view = childTransform.GetComponent<ViewScript>();

                    if (view != null)
                    {
                        view.TurnOff();
                        view.DisableInteraction();
                        views.Add(view);
                    }
                }
                if (childTransform.tag == "PuzzleView")
                {
                    ViewScript view = childTransform.GetComponent<ViewScript>();

                    if (view != null)
                    {
                        view.TurnOff();
                        view.DisableInteraction();
                        puzzleViews.Add(view);
                    }
                }
            }
            int numberOfWindows = views.Count;

            //for(int j = 0; j < views.Count; j++) // enable interaction for all 
                //views[j].EnableInteraction();

            if (numberOfWindows == 3)
            {
                List<Texture> rawImageTextures = new List<Texture>();
                List<int> rand2 = generateUniqueRandoms(3, 1); // random order
                for (int j = 0; j < 2; j++) // turn on 2 random views
                {
                    views[rand2[j]].TurnOn();
                    rawImageTextures.Add(views[rand2[j]].gameObject.transform.GetChild(1).GetChild(0).GetComponent<RawImage>().texture); // save icons
                }
                puzzleViews[rand2[1]].TurnOn(); // turn on 2 other puzzle views
                puzzleViews[rand2[2]].TurnOn();
                puzzleViews[rand2[1]].gameObject.transform.GetChild(1).GetChild(0).GetComponent<RawImage>().texture = rawImageTextures[0]; // swap icons
                puzzleViews[rand2[2]].gameObject.transform.GetChild(1).GetChild(0).GetComponent<RawImage>().texture = rawImageTextures[1];

                //wait until the last swap happens and icons matches
                yield return new WaitUntil(() => checkIcons(views, puzzleViews));

            }
            else if (numberOfWindows == 6)
            {
                List<int> rand3 = generateUniqueRandoms(6, 1);
                for (int j = 0; j < 3; j++) // turn on 3 random views
                    views[rand3[j]].TurnOn();

                //wait until the last swap happens.. ?
                yield return new WaitUntil(() => !views[rand3[0]].GetComponent<Toggle>().isOn && !views[rand3[1]].GetComponent<Toggle>().isOn && !views[rand3[2]].GetComponent<Toggle>().isOn);

            }
            else // numberOfWindows == 12
            {
                List<int> rand5 = generateUniqueRandoms(12, 1);
                for (int j = 0; j < 5; j++) // turn on 5 random views
                    views[rand5[j]].TurnOn();

                //wait until the last swap happens.. ?
                yield return new WaitUntil(() => !views[rand5[0]].GetComponent<Toggle>().isOn && !views[rand5[1]].GetComponent<Toggle>().isOn && !views[rand5[2]].GetComponent<Toggle>().isOn && !views[rand5[3]].GetComponent<Toggle>().isOn && !views[rand5[4]].GetComponent<Toggle>().isOn);

            }

            //for (int j = 0; j < views.Count; j++) // disable interaction for all 
                //views[j].DisableInteraction();

            yield return new WaitForSeconds(5);
            layout.SetActive(false);

        }
    }


    private bool checkIcons(List<ViewScript> views, List<ViewScript> puzzleViews)
    {
        bool solved = false;
        for(int i = 0; i < views.Count; i++)
        {
            if (views[i].Status())
            {
                Texture viewTexture = views[i].gameObject.transform.GetChild(1).GetChild(0).GetComponent<RawImage>().texture;
                Texture puzzleViewTexture = puzzleViews[i].gameObject.transform.GetChild(1).GetChild(0).GetComponent<RawImage>().texture;
                if (!viewTexture.name.Equals(puzzleViewTexture.name))
                    return false;
                else if (i == views.Count - 1)
                    return true;
            }
        }
        return solved;
    }

    // Update is called once per frame
    void Update()
    {
    }
}
